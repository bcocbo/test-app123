# tes-app-123

Aplicación desplegada con ArgoCD y GitOps.

## Información del Despliegue

| Campo | Valor |
|-------|-------|
| **Tipo** | custom (python) |
| **Namespace** | `dev` |
| **Entorno** | `dev` |
| **ECR Repository** | `tes-app-123` |
| **Chart** | [eks_baseline_chart_Helm](https://github.com/bcocbo/eks_baseline_chart_Helm) |
| **Réplicas** | 1 |

## Arquitectura GitOps

```
test-app123 (este repo)          gitops-apps (configuración)
├── app.py                       ├── argocd/applications/dev/tes-app-123.yaml
├── Dockerfile                   ├── values/dev/tes-app-123/values.yaml
└── .github/workflows/           └── values/preview/values.yaml
    ├── ci.yaml                      (values base para previews)
    ├── ci-preview.yaml
    └── ci-preview-cleanup.yaml
```

## CI/CD Pipelines

### Pipeline Principal (`ci.yaml`)

Se ejecuta en cada push a `main`:

1. **Build** — Construye la imagen Docker
2. **Push** — Sube a ECR con tag `{branch}-{short-sha}-{run-number}`
3. **PR al GitOps** — Crea un PR en `gitops-apps` actualizando el image tag en `values/dev/tes-app-123/values.yaml`
4. **Deploy** — Al mergear el PR, ArgoCD sincroniza automáticamente

### Pipeline Preview (`ci-preview.yaml`)

Se ejecuta cuando un PR hacia `main` tiene el label `preview`:

1. **Build** — Construye la imagen Docker
2. **Push** — Sube a ECR con tag `pr-{number}-{short-sha}`
3. **ArgoCD** — El ApplicationSet detecta el PR y crea un ambiente efímero

**No modifica el repo de gitops.** La imagen se resuelve por convención de tag.

### Pipeline Cleanup (`ci-preview-cleanup.yaml`)

Se ejecuta cuando se cierra un PR:

1. **ArgoCD** — Elimina automáticamente la Application, namespace y recursos
2. **ECR** — Limpia las imágenes `pr-{number}-*` del registry

## Preview Environments (Ambientes Efímeros)

### Cómo funciona

```
Developer abre PR con label "preview"
    │
    ▼
CI: build → push ECR (tag: pr-42-a1b2c3d)
    │
    │  (no toca el repo de gitops)
    │
    ▼
ArgoCD PR Generator: detecta PR con label "preview"
    │
    ├── Imagen: ECR/tes-app-123:pr-{{number}}-{{head_short_sha}}
    ├── Values base: values/preview/values.yaml (main, fijo)
    ├── Parameters sobreescriben: image, name, namespace
    │
    ▼
Crea namespace preview-{branch_slug}-{number} y despliega
    │
    ▼
Developer cierra/mergea PR → ambiente destruido automáticamente
```

### Convención de tag

El CI y el ApplicationSet acuerdan el formato de tag:

| Componente | Formato |
|------------|---------|
| CI genera | `pr-{PR_NUMBER}-{SHORT_SHA}` |
| ApplicationSet construye | `pr-{{number}}-{{head_short_sha}}` |

Ejemplo: `pr-42-a1b2c3d` — coinciden sin comunicación entre repos.

### Usar preview

1. Crea un branch y abre un PR hacia `main`
2. Agrega el label `preview` al PR
3. El CI construye la imagen y ArgoCD despliega el ambiente
4. Verifica:
   ```bash
   kubectl get pods -n preview-{branch_slug}-{number}
   kubectl get svc -n preview-{branch_slug}-{number}
   ```
5. Al cerrar/mergear el PR, todo se limpia automáticamente

## Despliegue Manual

### Verificar estado

```bash
# Estado en ArgoCD
argocd app get tes-app-123

# Pods
kubectl get pods -n dev -l app=tes-app-123

# Logs
kubectl logs -n dev -l app=tes-app-123 --tail=50
```

### Acceso local

```bash
kubectl port-forward -n dev svc/tes-app-123 8080:80
# http://localhost:8080
```

## Configuración Requerida

### Secretos de GitHub

| Secreto | Descripción |
|---------|-------------|
| `AWS_ROLE_ARN` | Rol de IAM para acceder a ECR |
| `GITOPS_TOKEN` | Token para crear PRs en gitops-apps |

Ver `.github/SETUP.md` para instrucciones detalladas.

---
Generado por Backstage Software Templates
