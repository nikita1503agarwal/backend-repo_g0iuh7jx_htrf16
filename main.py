import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List

from database import create_document
from schemas import ContactMessage

app = FastAPI(title="Oboloi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Oboloi backend running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/products")
def get_products():
    """Return a curated list of products to showcase on the site."""
    products = [
        {
            "id": "p1",
            "name": "Oboloi Core",
            "tagline": "Rapid app scaffolding and delivery",
            "description": "A developer toolkit that accelerates product delivery with ready-to-use building blocks, CI templates, and best practices baked in.",
            "links": {"learn_more": "https://example.com/core"}
        },
        {
            "id": "p2",
            "name": "Pulse Analytics",
            "tagline": "Real-time product analytics",
            "description": "Privacy-first analytics with feature flags, cohorts, and dashboards designed for fast-growing teams.",
            "links": {"learn_more": "https://example.com/pulse"}
        },
        {
            "id": "p3",
            "name": "Atlas Cloud",
            "tagline": "Deploy anything, anywhere",
            "description": "A multi-cloud deployment layer with blue/green releases, secrets management, and cost insights.",
            "links": {"learn_more": "https://example.com/atlas"}
        }
    ]
    return {"products": products}


@app.get("/api/projects")
def get_projects():
    """Return a curated list of recent projects/case studies."""
    projects = [
        {
            "id": "c1",
            "title": "E-commerce Revamp",
            "client": "RetailCo",
            "summary": "Migrated legacy monolith to a modern micro-frontend architecture with a blazing-fast checkout.",
            "results": [
                "+28% conversion",
                "-45% page load time",
                "Zero downtime migration"
            ]
        },
        {
            "id": "c2",
            "title": "Fintech KYC Automation",
            "client": "FinEdge",
            "summary": "Automated KYC/AML workflows with auditable trails and ML-assisted verification.",
            "results": [
                "3x faster onboarding",
                "99.98% accuracy",
                "SOC2-ready controls"
            ]
        },
        {
            "id": "c3",
            "title": "Healthcare Scheduling Platform",
            "client": "MediLink",
            "summary": "Built a HIPAA-compliant scheduling and telehealth platform across web and mobile.",
            "results": [
                "Launched in 12 weeks",
                "Seamless EHR integration",
                "99.95% uptime"
            ]
        }
    ]
    return {"projects": projects}


@app.post("/api/contact")
def submit_contact(payload: ContactMessage):
    """Store contact messages for follow up."""
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        # Still return a success to the user but indicate storage issue
        raise HTTPException(status_code=500, detail=f"Unable to store message: {str(e)[:120]}")


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
