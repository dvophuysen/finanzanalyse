from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .seed import seed
from .services import analytics, csv_import
from .services.categorization import categorize, learn_from_user_correction

app = FastAPI(title="Finanzanalyse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    db_url = settings.database_url
    if db_url.startswith("sqlite"):
        path = db_url.split("sqlite:///")[-1].lstrip("/")
        if path:
            Path("/" + os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)


api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": settings.llm_provider}


# --- Konten ---

@api.get("/accounts", response_model=list[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).order_by(models.Account.name).all()


@api.post("/accounts", response_model=schemas.AccountOut)
def create_account(payload: schemas.AccountIn, db: Session = Depends(get_db)):
    acc = models.Account(**payload.model_dump())
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


# --- Kategorien ---

@api.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.name).all()


@api.post("/categories", response_model=schemas.CategoryOut)
def create_category(payload: schemas.CategoryIn, db: Session = Depends(get_db)):
    cat = models.Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# --- Transaktionen ---

@api.get("/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(
    account_id: int | None = None,
    category_id: int | None = None,
    uncategorized: bool = False,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    q = db.query(models.Transaction).order_by(models.Transaction.booking_date.desc())
    if account_id:
        q = q.filter(models.Transaction.account_id == account_id)
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    if uncategorized:
        q = q.filter(models.Transaction.category_id.is_(None))
    return q.limit(limit).all()


@api.patch("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(
    tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(get_db)
):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(404, "Transaktion nicht gefunden")
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        tx.category_id = data["category_id"]
        tx.category_source = "user"
        tx.category_confidence = Decimal("1.0")
        learn_from_user_correction(db, tx)
    if "notes" in data:
        tx.notes = data["notes"]
    if "is_transfer" in data:
        tx.is_transfer = bool(data["is_transfer"])
    db.commit()
    db.refresh(tx)
    return tx


# --- Import ---

@api.post("/import/csv", response_model=schemas.ImportResult)
async def import_csv(
    account_id: int = Form(...),
    file: UploadFile = File(...),
    use_llm: bool = Form(True),
    db: Session = Depends(get_db),
):
    account = db.get(models.Account, account_id)
    if not account:
        raise HTTPException(404, "Konto nicht gefunden")

    raw = await file.read()
    try:
        parsed = csv_import.parse_csv(raw)
    except ValueError as e:
        raise HTTPException(400, str(e))

    imported = duplicates = skipped = 0
    for p in parsed:
        existing = (
            db.query(models.Transaction)
            .filter(
                models.Transaction.account_id == account_id,
                models.Transaction.external_id == p.external_id,
            )
            .first()
        )
        if existing:
            duplicates += 1
            continue

        tx = models.Transaction(
            account_id=account_id,
            booking_date=p.booking_date.date(),
            value_date=p.value_date.date() if p.value_date else None,
            amount=p.amount,
            currency=account.currency,
            counterparty=p.counterparty,
            purpose=p.purpose,
            raw_text=p.raw_text,
            external_id=p.external_id,
        )
        try:
            categorize(db, tx, use_llm=use_llm)
        except Exception:
            pass
        db.add(tx)
        try:
            db.flush()
            imported += 1
        except IntegrityError:
            db.rollback()
            skipped += 1

    db.commit()
    return schemas.ImportResult(
        imported=imported, skipped=skipped, duplicates=duplicates, account_id=account_id
    )


@api.post("/transactions/{tx_id}/recategorize", response_model=schemas.TransactionOut)
def recategorize(tx_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(404, "Transaktion nicht gefunden")
    tx.category_id = None
    tx.category_source = None
    tx.category_confidence = None
    categorize(db, tx, use_llm=True)
    db.commit()
    db.refresh(tx)
    return tx


# --- Analytics ---

@api.get("/analytics/cashflow")
def cashflow(months: int = 12, db: Session = Depends(get_db)):
    return analytics.monthly_cashflow(db, months=months)


@api.get("/analytics/breakdown")
def breakdown(start: date | None = None, end: date | None = None, db: Session = Depends(get_db)):
    return analytics.category_breakdown(db, start=start, end=end)


# --- Ziele ---

@api.get("/goals", response_model=list[schemas.GoalOut])
def list_goals(db: Session = Depends(get_db)):
    return db.query(models.Goal).order_by(models.Goal.priority).all()


@api.post("/goals", response_model=schemas.GoalOut)
def create_goal(payload: schemas.GoalIn, db: Session = Depends(get_db)):
    goal = models.Goal(**payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


app.include_router(api)


# --- Statisches Frontend ausliefern (für HA-Add-on / Single-Container) ---

STATIC_DIR = Path(os.environ.get("STATIC_DIR", "/app/static"))


def _serve_html(file: Path, request: Request) -> Response:
    ingress = request.headers.get("X-Ingress-Path", "").rstrip("/")
    base = (ingress + "/") if ingress else "/"
    html = file.read_text(encoding="utf-8")
    html = html.replace('="/_next/', '="_next/').replace("='/_next/", "='_next/")
    html = html.replace('href="/favicon', 'href="favicon')
    html = html.replace("<head>", f'<head><base href="{base}">', 1)
    return Response(content=html, media_type="text/html")


if STATIC_DIR.exists():
    app.mount("/_next", StaticFiles(directory=STATIC_DIR / "_next"), name="next-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str, request: Request):
        if full_path:
            candidate = STATIC_DIR / full_path
            if candidate.is_file() and candidate.suffix != ".html":
                return FileResponse(candidate)
            html = STATIC_DIR / f"{full_path}.html"
            if html.is_file():
                return _serve_html(html, request)
        index = STATIC_DIR / "index.html"
        if index.is_file():
            return _serve_html(index, request)
        raise HTTPException(404)
