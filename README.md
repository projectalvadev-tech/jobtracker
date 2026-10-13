# JobTracker

API para registrar postulaciones laborales y ver qué tecnologías se repiten más en las ofertas.
Proyecto de portafolio pensado para practicar el stack que piden las ofertas de TI en Chile:
Docker, CI/CD (Jenkins), IaC (Terraform), Kubernetes, cloud (AWS) y observabilidad.

## Stack

| Área | Tecnología | Estado |
|---|---|---|
| API | FastAPI, SQLAlchemy 2, PostgreSQL | ✅ Fase 1 |
| Tests y calidad | pytest, ruff | ✅ Fase 1 |
| Contenedores | Docker multi-stage, docker compose | ✅ Fase 1 |
| CI/CD | Jenkins + GitHub Actions | ✅ Fase 2 |
| Seguridad | Trivy ✅ · SonarQube ⏳ | 🔄 Fase 3 |
| IaC / Cloud | Terraform, AWS | ⏳ Fase 4 |
| Orquestación | Kubernetes, Helm | ⏳ Fase 5 |
| Observabilidad | Prometheus, Grafana | ⏳ Fase 6 |

## Cómo correrlo

```bash
cp .env.example .env      # y cambia la contraseña
make up                   # levanta API + PostgreSQL
```

- Documentación interactiva: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Ejemplo:

```bash
curl -X POST localhost:8000/applications -H "Content-Type: application/json" -d '{
  "company": "Acme", "position": "DevOps Jr", "source": "computrabajo",
  "stack": ["Docker", "Jenkins", "Terraform"]
}'
curl localhost:8000/applications/stats
```

## Desarrollo local

```bash
make install
source .venv/bin/activate
make test      # usa SQLite en memoria, no requiere Docker
make lint
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/applications` | Crear postulación |
| GET | `/applications?status=interview` | Listar (filtro y paginación) |
| GET | `/applications/stats` | Totales por estado y tecnologías más pedidas |
| GET/PATCH/DELETE | `/applications/{id}` | Ver, editar, borrar |
| GET | `/health` | Estado de la app y la base de datos |

## Decisiones

- **Docker multi-stage + usuario no root**: imagen más liviana y más segura.
- **Healthcheck en compose**: la API espera a que PostgreSQL esté listo.
- **Tests con SQLite en memoria**: rápidos, y correrán igual en el pipeline.
- **`create_all` al iniciar**: suficiente para la Fase 1; se reemplazará por Alembic.
