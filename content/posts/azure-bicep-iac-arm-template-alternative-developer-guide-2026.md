---
title: "Azure Bicep IaC ARM Template Alternative Developer Guide 2026"
date: 2026-05-18T18:03:30+00:00
tags: ["azure", "bicep", "infrastructure-as-code", "arm-templates", "devops"]
description: "Azure Bicep이 ARM JSON 템플릿을 대체하는 이유와 마이그레이션, 모듈, CI/CD 통합 방법을 다루는 완전한 개발자 가이드."
draft: false
cover:
  image: "/images/azure-bicep-iac-arm-template-alternative-developer-guide-2026.png"
  alt: "Azure Bicep IaC ARM Template Alternative Developer Guide 2026"
  relative: false
schema: "schema-azure-bicep-iac-arm-template-alternative-developer-guide-2026"
---

Azure Bicep은 ARM JSON 템플릿의 공식 후속 언어로, 동일한 Azure Resource Manager 엔진 위에서 동작하면서 코드 크기를 절반으로 줄이고 IntelliSense와 타입 안전성을 제공합니다. Microsoft는 2026년 현재 모든 신규 ARM 배포에 Bicep을 기본 권장 언어로 채택했습니다.

## What Is Azure Bicep and Why It Replaces ARM Templates in 2026

Azure Bicep은 Azure Resource Manager(ARM) 위에서 동작하는 도메인 특화 언어(DSL)로, JSON 기반 ARM 템플릿의 복잡성을 제거하고 선언형 인프라 정의를 더 간결하고 읽기 쉬운 구문으로 표현합니다. Microsoft가 2020년에 발표한 이후 2026년에는 ARM 템플릿을 완전히 대체하는 1순위 Azure IaC 도구로 자리잡았습니다. Fortune 500 기업의 약 85%가 Azure를 사용하고 있으며, 그중 점점 더 많은 팀이 Bicep으로 전환하고 있습니다. Q4 2025 기준 Azure는 전체 엔터프라이즈 클라우드 인프라 지출의 21%를 차지했는데, 이는 인프라 자동화 수요가 지속적으로 증가하고 있음을 의미합니다. Bicep 코드는 동일한 ARM JSON 템플릿에 비해 약 절반의 크기로, 제조업체 한 곳은 Bicep 도입 후 인프라 프로비저닝 시간을 70% 단축했습니다. ARM 템플릿이 사라지는 것은 아니지만, Microsoft는 공식 문서에서 모든 새로운 워크플로우에 Bicep 사용을 명시적으로 권고합니다. Bicep v0.43.1(2026)에서는 `like()`와 `distinct()` 함수가 추가되어 고급 패턴 매칭과 데이터 처리가 가능해졌으며, Azure Verified Modules(AVM)를 통해 엔터프라이즈 수준의 사전 검증된 모듈을 즉시 활용할 수 있습니다.

### ARM 템플릿의 한계

ARM 템플릿은 강력하지만 장황한 JSON 구조, 반복적인 `dependsOn` 선언, 조건부 로직의 가독성 부족이라는 고질적 문제가 있었습니다. 수백 줄의 JSON을 디버깅하는 것은 팀 생산성을 크게 떨어뜨렸고, 재사용 가능한 모듈 시스템도 제한적이었습니다. Bicep은 이 모든 문제를 주소 지정하면서도 ARM 엔진 위에서 직접 트랜스파일되기 때문에 별도의 상태 파일 없이 Azure의 네이티브 배포 메커니즘을 그대로 활용합니다.

## Bicep vs ARM Templates: Syntax and Code Size Comparison

Bicep은 ARM JSON 대비 코드 크기를 평균 50% 줄이며, 동일한 리소스를 훨씬 읽기 쉬운 방식으로 표현합니다. 이 차이는 단순한 스타일 문제가 아니라 실질적인 유지보수 비용 절감으로 이어집니다. `dependsOn`을 수동으로 작성하지 않아도 되고, 변수와 파라미터에 타입이 지정되며, 리소스 간 참조는 심볼릭 이름으로 처리됩니다. 대규모 엔터프라이즈 팀에서 수천 줄의 ARM JSON을 관리하던 것을 Bicep으로 전환하면 같은 인프라를 수백 줄로 표현할 수 있으며, CI 파이프라인에서 `az bicep build` 명령으로 ARM JSON으로 즉시 트랜스파일됩니다. Bicep 파일 자체는 버전 관리 시스템에서 관리하고, 배포 시에만 ARM JSON이 생성됩니다. 이 접근 방식은 상태 파일 없이 Azure 포털과의 완전한 호환성을 유지한다는 점에서 Terraform과 근본적으로 다릅니다.

다음은 Storage Account를 ARM JSON과 Bicep으로 비교한 예시입니다:

**ARM JSON (약 30줄):**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "storageAccountName": {
      "type": "string"
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[parameters('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ]
}
```

**Bicep (약 10줄):**
```bicep
param storageAccountName string
param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}
```

| 항목 | ARM JSON | Azure Bicep |
|------|----------|-------------|
| 평균 코드 크기 | 100% (기준) | ~50% |
| 타입 안전성 | 제한적 | 완전한 타입 추론 |
| IntelliSense | 부분적 | 전체 지원 |
| dependsOn | 수동 작성 | 자동 추론 |
| 모듈 재사용 | 연결된 템플릿 | 네이티브 모듈 |
| 상태 파일 | 없음 | 없음 |
| Azure 호환성 | 완전 | 완전 (ARM으로 트랜스파일) |

## Getting Started with Azure Bicep: Installation and First Deployment

Azure Bicep 시작은 세 단계로 완료됩니다: Azure CLI 설치(또는 업데이트), Bicep CLI 설치, VS Code Bicep 확장 설치. Azure CLI 2.20.0 이상이 설치된 환경에서는 `az bicep install` 하나로 Bicep CLI가 설치됩니다. VS Code Bicep 확장은 실시간 IntelliSense, 리소스 타입 자동 완성, 린팅, 포맷팅을 제공하며 2026년 기준 1,000만 건 이상 다운로드됩니다. 첫 번째 Bicep 배포는 리소스 그룹 레벨에서 `az deployment group create --resource-group myRG --template-file main.bicep --parameters storageAccountName=mystorage2026` 명령으로 실행됩니다. Bicep CLI는 자동으로 ARM JSON으로 트랜스파일한 후 배포를 진행하므로 개발자가 ARM JSON을 직접 작성할 필요가 없습니다. 타입 안전한 `.bicepparam` 파라미터 파일은 기존 ARM JSON `parameters.json`을 대체하며, VS Code에서 파라미터 타입 오류를 배포 전에 즉시 감지할 수 있습니다. 로컬 개발 환경에서는 `az bicep lint`로 모범 사례 위반을 사전에 확인하고, `az deployment group what-if`로 실제 인프라에 영향을 주지 않고 변경 사항을 미리 검토하는 것이 일반적인 워크플로우입니다.

```bash
# Azure CLI 및 Bicep 설치
az bicep install
az bicep version  # 현재 버전 확인

# 첫 배포 실행
az deployment group create \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters @parameters.json
```

### Bicep 파라미터 파일

Bicep은 `.bicepparam` 형식의 타입 안전한 파라미터 파일을 지원합니다:

```bicep
using './main.bicep'

param storageAccountName = 'mystorage2026prod'
param location = 'eastus'
param sku = 'Standard_GRS'
```

이 형식은 기존 ARM JSON 파라미터 파일보다 훨씬 간결하며, VS Code에서 타입 오류를 즉시 감지합니다.

## Understanding Bicep Modules and the Azure Verified Modules (AVM) Registry

Bicep 모듈은 독립적인 `.bicep` 파일로 분리된 재사용 가능한 인프라 컴포넌트입니다. 모듈 시스템은 로컬 파일 참조, 퍼블릭 레지스트리(Bicep Public Registry), 프라이빗 ACR(Azure Container Registry) 세 가지 소스를 지원합니다. Azure Verified Modules(AVM)는 Microsoft가 직접 빌드하고 테스트한 엔터프라이즈 수준의 Bicep 모듈 컬렉션으로, Public Bicep Registry를 통해 배포됩니다. 2026년 기준 AVM은 Storage, Networking, Compute, Security 등 핵심 Azure 서비스를 커버하는 100개 이상의 모듈을 포함합니다. AVM은 단순한 리소스 래퍼가 아니라 보안 기본값, 진단 설정, Private Endpoint, RBAC 할당을 사전 통합한 프로덕션 준비 완료 모듈입니다. Microsoft Platform Landing Zone(PLZ)도 AVM 기반으로 리팩토링되어, 대규모 엔터프라이즈 Azure 랜딩 존 배포의 표준 방식이 되었습니다.

```bicep
// AVM Storage Account 모듈 사용 예시
module storage 'br/public:avm/res/storage/storage-account:0.9.0' = {
  name: 'storageDeployment'
  params: {
    name: storageAccountName
    location: location
    skuName: 'Standard_GRS'
    allowBlobPublicAccess: false
    privateEndpoints: [
      {
        subnetResourceId: subnet.id
        service: 'blob'
      }
    ]
  }
}
```

### 프라이빗 모듈 레지스트리 구축

팀 내 공유 Bicep 모듈은 Azure Container Registry에 퍼블리시하여 버전 관리할 수 있습니다:

```bash
# ACR에 모듈 퍼블리시
az bicep publish \
  --file modules/storage.bicep \
  --target br:myregistry.azurecr.io/bicep/storage:v1.2.0
```

이 패턴은 대규모 조직에서 인프라 팀이 검증된 모듈을 중앙에서 관리하고, 애플리케이션 팀이 버전 고정된 모듈을 참조하게 하는 표준 방식입니다.

## Migrating Existing ARM Templates to Bicep: The Five-Phase Workflow

ARM에서 Bicep으로 마이그레이션하는 Microsoft 권장 5단계 워크플로우는 준비(Convert), 마이그레이션(Migrate), 리팩토링(Refactor), 검증(Test), 배포(Deploy) 순서로 진행됩니다. `az bicep decompile` 명령은 기존 ARM JSON을 Bicep으로 자동 변환하지만, 생성된 코드는 항상 검토가 필요합니다. Decompile은 완벽하지 않으며 특히 `copy` 루프, 조건부 리소스, 중첩 템플릿 처리에서 수동 수정이 필요한 경우가 많습니다. 마이그레이션의 핵심은 단순히 구문을 변환하는 것이 아니라 Bicep의 모듈화, 타입 안전성, 선언적 패턴을 활용한 리팩토링을 병행하는 것입니다. 실제로 대형 ARM 템플릿 라이브러리를 Bicep으로 전환한 팀들은 단순 변환 후 코드 리뷰 없이 배포했다가 예상치 못한 차이가 발생한 사례를 보고했습니다.

**Phase 1: Convert (자동 변환)**
```bash
az bicep decompile --file azuredeploy.json
# 출력: azuredeploy.bicep
```

**Phase 2: Migrate (수동 검토)**
- Decompile 결과에서 `//WARNING` 주석 확인
- 하드코딩된 값을 파라미터로 추출
- 반복 리소스를 `for` 루프로 변환

**Phase 3: Refactor (모듈화)**
```bicep
// 단일 파일에서 모듈 분리
module network './modules/network.bicep' = {
  name: 'networkDeployment'
  params: {
    vnetAddressPrefix: '10.0.0.0/16'
  }
}
```

**Phase 4: Test (what-if 검증)**
```bash
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @prod.bicepparam
```

**Phase 5: Deploy (단계적 배포)**
- 비프로덕션 환경 먼저 배포
- ARM JSON 템플릿과 결과 비교 검증
- 프로덕션 롤아웃

## Azure Deployment Stacks: Lifecycle Management for Production Infrastructure

Azure Deployment Stacks는 2024년 GA된 기능으로, Bicep 배포된 리소스 컬렉션을 단일 단위로 관리하는 네이티브 상태 관리 메커니즘입니다. Terraform의 `terraform destroy`와 유사하게, 스택에서 제거된 리소스를 자동으로 삭제하거나 분리하는 정책을 정의할 수 있어 인프라 드리프트를 방지합니다. Deployment Stacks는 별도 상태 파일 없이 Azure Resource Manager 자체가 관리 단위를 추적합니다. `denySettings`를 통해 스택 외부에서 리소스 수정을 차단하는 가드레일을 설정할 수 있어 컴플라이언스 요구사항이 있는 엔터프라이즈 환경에 특히 유용합니다. 이 기능은 Bicep이 Terraform과 경쟁하는 핵심 차별화 요소 중 하나로, Azure 전용 워크로드에서 상태 파일 없이 완전한 라이프사이클 관리를 가능하게 합니다.

```bash
# Deployment Stack 생성
az stack group create \
  --name myProductionStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @prod.bicepparam \
  --action-on-unmanage deleteAll \
  --deny-settings-mode denyWriteAndDelete

# 스택 업데이트 (제거된 리소스 자동 정리)
az stack group update \
  --name myProductionStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @prod.bicepparam
```

### Deployment Stacks vs Terraform State

| 항목 | Azure Deployment Stacks | Terraform State |
|------|------------------------|-----------------|
| 상태 저장 위치 | Azure Resource Manager | 로컬/원격 backend |
| 멀티클라우드 | 불가 | 가능 |
| 드리프트 감지 | ARM과 일치 | `terraform plan` |
| 리소스 잠금 | denySettings | 없음 (별도 설정 필요) |
| 비용 | 추가 비용 없음 | backend 비용 발생 가능 |

## CI/CD Integration: Bicep with GitHub Actions and Azure DevOps Pipelines

Bicep CI/CD 통합은 `az deployment group what-if` 명령을 PR 단계에서 실행하여 인프라 변경 사항을 미리 검토하는 패턴이 표준입니다. GitHub Actions에서는 `azure/login`, `azure/arm-deploy` 액션을 통해 OIDC 기반 인증으로 비밀 없이 Azure에 배포할 수 있습니다. 2026년 GitHub Actions Bicep 워크플로우의 권장 패턴은 린트(`az bicep lint`) → 빌드(`az bicep build`) → what-if → 배포 승인 → 배포의 5단계 파이프라인입니다. Azure DevOps는 `AzureResourceManagerTemplateDeployment` 태스크가 Bicep을 네이티브로 지원하므로 별도 변환 없이 직접 `.bicep` 파일을 참조할 수 있습니다. 두 플랫폼 모두 환경별 파라미터 파일(`dev.bicepparam`, `staging.bicepparam`, `prod.bicepparam`)과 서비스 프린시팔 OIDC를 조합하는 것이 2026년 베스트 프랙티스입니다.

**GitHub Actions 워크플로우 예시:**
```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Lint Bicep
        run: az bicep lint --file main.bicep
      
      - name: What-If Preview
        uses: azure/arm-deploy@v2
        with:
          resourceGroupName: myRG
          template: main.bicep
          parameters: environments/${{ github.ref_name }}.bicepparam
          additionalArguments: "--what-if"

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Deploy Bicep
        uses: azure/arm-deploy@v2
        with:
          resourceGroupName: myRG
          template: main.bicep
          parameters: environments/prod.bicepparam
```

### Azure DevOps 파이프라인

```yaml
- task: AzureResourceManagerTemplateDeployment@3
  inputs:
    deploymentScope: 'Resource Group'
    azureResourceManagerConnection: 'MyServiceConnection'
    resourceGroupName: 'myRG'
    location: 'East US'
    templateLocation: 'Linked artifact'
    csmFile: 'infra/main.bicep'
    csmParametersFile: 'infra/environments/prod.bicepparam'
    deploymentMode: 'Incremental'
```

## Bicep vs Terraform for Azure: When to Choose Each Tool

Bicep과 Terraform 중 선택은 팀의 멀티클라우드 전략과 기존 기술 스택에 따라 달라집니다. Azure 전용 환경에서는 Bicep이 더 빠른 새 리소스 지원(ARM API와 동시), 상태 파일 관리 불필요, Microsoft 공식 지원, AVM 생태계 접근성 면에서 우세합니다. Terraform은 AWS, GCP, Azure를 동일한 워크플로우로 관리해야 하는 멀티클라우드 팀, Terraform Cloud/Enterprise의 협업 기능이 필요한 팀, HCL에 이미 투자한 팀에게 더 적합합니다. 2026년 기준 Pulumi는 TypeScript/Python으로 인프라를 코드처럼 작성하고 싶은 개발자 팀의 제3 선택지로 부상했지만, Azure 전용 생태계에서 Bicep의 AVM 지원과 Deployment Stacks는 Terraform이 따라잡기 어려운 차별점을 만들고 있습니다.

| 기준 | Azure Bicep | Terraform | Pulumi |
|------|-------------|-----------|--------|
| Azure 리소스 지원 속도 | 가장 빠름 (ARM 동시) | 지연 있음 | 지연 있음 |
| 멀티클라우드 | 불가 | 가능 | 가능 |
| 상태 파일 | 불필요 | 필요 | 필요 |
| 언어 | Bicep DSL | HCL | TypeScript/Python/Go |
| 엔터프라이즈 모듈 | AVM (Microsoft 공식) | Terraform Registry | Pulumi Registry |
| 학습 곡선 | 낮음 (Azure 개발자) | 중간 | 높음 |
| 비용 | 무료 | OSS 무료 / Cloud 유료 | 무료 |

**Bicep을 선택해야 하는 경우:**
- Azure 전용 워크로드
- 새 Azure 서비스를 즉시 사용해야 할 때
- ARM 템플릿 마이그레이션
- Microsoft 지원이 중요한 엔터프라이즈 환경

**Terraform을 선택해야 하는 경우:**
- 멀티클라우드 환경 (AWS + Azure 등)
- 기존 Terraform 코드베이스가 있는 경우
- Terraform Cloud의 협업 기능이 필요한 경우

## Bicep Best Practices for Enterprise Teams in 2026

엔터프라이즈 Bicep 운영의 핵심은 일관된 모듈화, 강제 린팅, 환경별 파라미터 분리, Azure Policy와의 통합 네 가지입니다. Bicep v0.43.1(2026)에서 추가된 `like()`와 `distinct()` 함수는 고급 패턴 매칭과 데이터 처리를 지원하여 복잡한 조건부 배포 로직을 더 명확하게 표현할 수 있게 되었습니다. 모든 Bicep 배포에는 리소스 태깅 정책, 진단 설정, Private Endpoint 구성을 AVM 모듈을 통해 표준화하는 것이 권장됩니다. `bicepconfig.json` 파일로 프로젝트 전체에 린팅 규칙을 강제하고, PR 파이프라인에서 `az bicep lint --diagnostics-format sarif` 출력을 GitHub Security 탭에 업로드하는 패턴이 일반화되고 있습니다.

```json
// bicepconfig.json - 팀 린팅 표준
{
  "analyzers": {
    "core": {
      "enabled": true,
      "verbose": false,
      "rules": {
        "no-hardcoded-env-urls": {
          "level": "error"
        },
        "no-unused-params": {
          "level": "warning"
        },
        "secure-parameter-default": {
          "level": "error"
        },
        "use-resource-id-functions": {
          "level": "warning"
        }
      }
    }
  },
  "moduleAliases": {
    "br": {
      "modules": {
        "registry": "myregistry.azurecr.io",
        "modulePath": "bicep"
      }
    }
  }
}
```

### 엔터프라이즈 디렉토리 구조

```
infra/
├── main.bicep              # 루트 오케스트레이터
├── bicepconfig.json        # 린팅 규칙
├── modules/                # 팀 내부 모듈
│   ├── network.bicep
│   ├── storage.bicep
│   └── app-service.bicep
├── environments/           # 환경별 파라미터
│   ├── dev.bicepparam
│   ├── staging.bicepparam
│   └── prod.bicepparam
└── scripts/                # 배포 자동화 스크립트
    └── deploy.sh
```

### 보안 베스트 프랙티스

- `@secure()` 데코레이터로 민감한 파라미터 처리 (ARM JSON으로 트랜스파일 시 자동으로 `secureString` 타입)
- Key Vault 참조를 파라미터 파일에서 직접 사용 (`reference()` 대신 Key Vault secrets reference)
- `denySettings`가 활성화된 Deployment Stacks로 스택 외부 수정 차단
- PR 파이프라인에 `what-if` 필수 적용으로 의도치 않은 리소스 삭제 방지

## Frequently Asked Questions About Azure Bicep

**Q: ARM 템플릿은 언제까지 지원되나요?**

ARM 템플릿(JSON)은 Azure Resource Manager의 기반이므로 공식 지원 종료 일정이 발표되지 않았습니다. 하지만 Microsoft는 2026년 현재 모든 새 기능과 문서를 Bicep 중심으로 개발하고 있으며, ARM JSON 템플릿 직접 작성보다 Bicep을 명시적으로 권장합니다. 기존 ARM 템플릿은 계속 동작하지만 신규 프로젝트는 Bicep으로 시작하는 것이 바람직합니다.

**Q: Bicep 파일을 ARM JSON으로 변환할 수 있나요?**

네. `az bicep build --file main.bicep` 명령으로 언제든지 ARM JSON으로 트랜스파일할 수 있습니다. 실제로 Azure는 Bicep 파일을 직접 배포하더라도 내부적으로 ARM JSON으로 변환하여 처리합니다. 반대로 `az bicep decompile --file azuredeploy.json`으로 ARM JSON을 Bicep으로 역변환할 수 있지만, 복잡한 템플릿에서는 수동 검토가 필요합니다.

**Q: Bicep과 Terraform을 같은 프로젝트에서 함께 사용할 수 있나요?**

기술적으로는 가능하지만 권장하지 않습니다. 일부 팀은 Azure Kubernetes Service 클러스터는 Bicep으로, Kubernetes 내부 리소스는 Helm/Terraform으로 관리하는 레이어 분리 전략을 사용합니다. 그러나 두 도구의 상태 관리 방식이 다르기 때문에 드리프트가 발생할 수 있습니다. Azure 전용 환경이라면 Bicep + Deployment Stacks로 통일하는 것이 운영 복잡성을 낮춥니다.

**Q: Azure Bicep의 유료 플랜이 있나요?**

Bicep은 완전히 무료이며 오픈소스(MIT 라이선스)입니다. Azure CLI, VS Code, GitHub Actions에서 추가 비용 없이 사용할 수 있습니다. Deployment Stacks도 추가 비용이 없으며, 배포된 Azure 리소스 자체 비용만 청구됩니다. Terraform Cloud처럼 협업 플랫폼 비용이 발생하지 않는 점이 Bicep의 비용 우위 중 하나입니다.

**Q: Bicep은 모든 Azure 서비스를 지원하나요?**

Bicep은 Azure Resource Manager API를 지원하는 모든 Azure 서비스를 배포할 수 있습니다. 새로운 Azure 서비스나 리소스 타입이 ARM API에 추가되면 즉시 Bicep에서 사용 가능합니다. `az provider list`와 `az bicep generate-params`로 최신 리소스 타입과 파라미터 스키마를 확인할 수 있습니다. Terraform의 경우 새 Azure 서비스가 공식 프로바이더에 반영되기까지 지연이 있지만, Bicep은 이 제약이 없습니다.
