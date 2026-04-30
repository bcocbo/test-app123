# CI/CD Setup Guide

Este repositorio incluye un workflow de GitHub Actions que automáticamente:
1. Construye la imagen Docker
2. La sube a Amazon ECR
3. Actualiza el repositorio GitOps con el nuevo tag de imagen

## 📋 Requisitos Previos

- Cuenta de AWS con acceso a ECR
- Repositorio ECR creado
- Repositorio GitOps configurado
- GitHub Actions habilitado

## 🔐 Configuración de Secretos

Debes configurar los siguientes secretos en GitHub:

### 1. AWS_ROLE_ARN-p

ARN del rol de IAM que GitHub Actions usará para acceder a AWS.

**Crear el rol:**

```bash
# Crear trust policy para GitHub Actions
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:bcocbo/*:*"
        }
      }
    }
  ]
}
EOF

# Crear el rol
aws iam create-role \
  --role-name GitHubActionsECRRole \
  --assume-role-policy-document file://trust-policy.json

# Adjuntar política para ECR
aws iam attach-role-policy \
  --role-name GitHubActionsECRRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser
```

**Agregar a GitHub:**
1. Ve a Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `AWS_ROLE_ARN`
4. Value: `arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsECRRole`

### 2. GITOPS_TOKEN

Token de GitHub con permisos para crear PRs en el repositorio GitOps.

**Crear el token:**
1. Ve a https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Selecciona scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Copia el token

**Agregar a GitHub:**
1. Ve a Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GITOPS_TOKEN`
4. Value: `ghp_...` (tu token)

## 🏗️ Crear Repositorio ECR

```bash
# Crear repositorio en ECR
aws ecr create-repository \
  --repository-name tes-app-123 \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Configurar lifecycle policy (opcional)
cat > lifecycle-policy.json <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF

aws ecr put-lifecycle-policy \
  --repository-name tes-app-123 \
  --lifecycle-policy-text file://lifecycle-policy.json
```

## 🔧 Configurar OIDC Provider (Primera vez)

Si es la primera vez que usas GitHub Actions con AWS, necesitas configurar el OIDC provider:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

## ✅ Verificar Configuración

1. **Verificar secretos:**
   ```bash
   # En tu repositorio, ve a Settings → Secrets and variables → Actions
   # Deberías ver:
   # - AWS_ROLE_ARN
   # - GITOPS_TOKEN
   ```

2. **Probar el workflow:**
   ```bash
   # Hacer un commit y push
   git add .
   git commit -m "test: Trigger CI/CD"
   git push origin main
   
   # Ver el workflow en GitHub Actions
   # https://github.com/bcocbo/tes-app-123/actions
   ```

## 📊 Flujo del Workflow

```
┌─────────────────┐
│  Push to main   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Checkout code   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Configure AWS   │
│ (OIDC)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Login to ECR    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build Docker    │
│ image           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Push to ECR     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Clone GitOps    │
│ repo            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update          │
│ values.yaml     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create PR       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ArgoCD detects  │
│ and deploys     │
└─────────────────┘
```

## 🐛 Troubleshooting

### Error: "Unable to assume role"
- Verifica que el `AWS_ROLE_ARN` sea correcto
- Verifica que el OIDC provider esté configurado
- Verifica que el trust policy incluya tu repositorio

### Error: "Permission denied to create PR"
- Verifica que el `GITOPS_TOKEN` tenga permisos de `repo`
- Verifica que el token no haya expirado

### Error: "Repository not found in ECR"
- Crea el repositorio ECR con el comando mostrado arriba
- Verifica que el nombre coincida con `ECR_REPOSITORY` en el workflow

## 📚 Referencias

- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
