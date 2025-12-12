# tes-app-123

Aplicación desplegada con ArgoCD y GitOps

## Información del Despliegue

- **Tipo**: custom (python)
- **Namespace**: `dev`
- **Entorno**: `dev`

- **Imagen**: Construida automáticamente por CI/CD

- **Réplicas**: 1

## Despliegue con ArgoCD

Esta aplicación se despliega automáticamente usando ArgoCD y GitOps.

### Verificar el Estado

```bash
# Ver el estado de la aplicación en ArgoCD
argocd app get tes-app-123

# Ver los pods desplegados
kubectl get pods -n dev -l app=tes-app-123

# Ver los logs
kubectl logs -n dev -l app=tes-app-123 --tail=50
```

### Acceder a la Aplicación

```bash
# Port forward para acceso local
kubectl port-forward -n dev svc/tes-app-123 8080:80

# Luego visita: http://localhost:8080
```


## CI/CD Automático

El pipeline de CI/CD se ejecuta automáticamente en cada push a `main`:

### Flujo Automático
1. **Build**: Construye la imagen Docker
2. **Push**: Sube la imagen a Amazon ECR
3. **Update**: Actualiza el tag en el repositorio GitOps
4. **Deploy**: ArgoCD detecta el cambio y despliega automáticamente

### Configuración Requerida

Antes de hacer push, configura los secretos de GitHub:
- `AWS_ROLE_ARN` - Rol de IAM para acceder a ECR
- `GITOPS_TOKEN` - Token para crear PRs en gitops-apps

Ver `.github/SETUP.md` para instrucciones detalladas.

### Tags de Imagen

Las imágenes se etiquetan con: `{branch}-{short-sha}-{run-number}`

Ejemplo: `main-a1b2c3d-42`

## Actualizar la Aplicación

### Opción 1: Automática (Recomendada)
Simplemente haz push de tus cambios a `main` y el CI/CD se encargará del resto.

### Opción 2: Manual
Modifica los values en el [repositorio GitOps](https://github.com/bcocbo/gitops-apps) y ArgoCD sincronizará automáticamente.



---
Generado por Backstage Software Templates
