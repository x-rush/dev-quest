# CI/CD流水线指南 (CI/CD Pipelines Guide)

> **PHP开发者视角**: 从手动部署到自动化CI/CD流程的转变，了解现代DevOps实践如何提升开发效率和代码质量。

## CI/CD基础概念

### 什么是CI/CD

**CI (Continuous Integration)** - 持续集成
- 自动化构建和测试
- 代码合并到主分支前验证
- 快速反馈和问题发现

**CD (Continuous Deployment)** - 持续部署
- 自动化部署到生产环境
- 减少人为错误
- 加速交付周期

### CI/CD的价值

1. **质量保证**: 自动化测试确保代码质量
2. **快速交付**: 自动化部署缩短发布周期
3. **风险控制**: 逐步发布和快速回滚
4. **团队协作**: 标准化流程和透明度
5. **成本节约**: 减少手动操作和错误修复成本

## GitHub Actions配置

### 1. 基础CI流水线

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run type checking
        run: npm run type-check

      - name: Run linting
        run: npm run lint

      - name: Run unit tests
        run: npm run test:unit
        env:
          NODE_ENV: test

      - name: Run integration tests
        run: npm run test:integration
        env:
          NODE_ENV: test

      - name: Upload coverage reports
        if: matrix.node-version == 18
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build
        env:
          NODE_ENV: production

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-files
          path: .next
          retention-days: 30
```

### 2. Docker构建和部署

```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /app
            docker-compose pull
            docker-compose up -d
            docker system prune -f

  deploy-production:
    needs: docker
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /app
            docker-compose pull
            docker-compose up -d
            docker system prune -f
```

### 3. Vercel自动部署

```yaml
# .github/workflows/vercel.yml
name: Vercel Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: vercel/action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./

      - name: Comment PR with preview URL
        uses: actions/github-script@v7
        with:
          script: |
            const { VERCEL_URL } = process.env
            if (VERCEL_URL) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `🚀 Preview deployment: ${VERCEL_URL}`
              })
            }
        env:
          VERCEL_URL: ${{ steps.deploy.outputs.preview-url }}

  deploy-production:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Vercel Production
        uses: vercel/action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: "--prod"
          working-directory: ./

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          BASE_URL: ${{ steps.deploy.outputs.production-url }}
```

## GitLab CI配置

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "18"
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

cache:
  paths:
    - node_modules/
    - .next/cache/

test:
  stage: test
  image: node:${NODE_VERSION}
  before_script:
    - npm ci
  script:
    - npm run type-check
    - npm run lint
    - npm run test:unit
    - npm run test:integration
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      junit:
        - junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG

deploy-staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $STAGING_USER@$STAGING_HOST "cd /app && docker-compose pull && docker-compose up -d"
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy-production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $PRODUCTION_USER@$PRODUCTION_HOST "cd /app && docker-compose pull && docker-compose up -d"
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

## 环境管理

### 1. 多环境配置

```yaml
# .github/workflows/environments.yml
name: Multi-Environment Deployment

on:
  push:
    branches: [main, develop, feature/*]
  pull_request:
    branches: [main]

jobs:
  determine-environment:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.env.outputs.environment }}
    steps:
      - id: env
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
          fi

  deploy:
    needs: determine-environment
    runs-on: ubuntu-latest
    environment: ${{ needs.determine-environment.outputs.environment }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup environment variables
        run: |
          if [[ "${{ needs.determine-environment.outputs.environment }}" == "production" ]]; then
            echo "NODE_ENV=production" >> $GITHUB_ENV
            echo "DOMAIN=example.com" >> $GITHUB_ENV
          elif [[ "${{ needs.determine-environment.outputs.environment }}" == "staging" ]]; then
            echo "NODE_ENV=production" >> $GITHUB_ENV
            echo "DOMAIN=staging.example.com" >> $GITHUB_ENV
          else
            echo "NODE_ENV=development" >> $GITHUB_ENV
            echo "DOMAIN=dev.example.com" >> $GITHUB_ENV
          fi

      - name: Deploy application
        run: |
          echo "Deploying to ${{ needs.determine-environment.outputs.environment }}"
          echo "Domain: ${{ env.DOMAIN }}"
          # 部署逻辑...
```

### 2. 环境变量管理

```yaml
# .github/workflows/secrets.yml
name: Secrets Management

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup environment
        run: |
          echo "DATABASE_URL=${{ secrets.DATABASE_URL }}" >> .env.production
          echo "NEXTAUTH_SECRET=${{ secrets.NEXTAUTH_SECRET }}" >> .env.production
          echo "STRIPE_SECRET_KEY=${{ secrets.STRIPE_SECRET_KEY }}" >> .env.production
          echo "AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}" >> .env.production
          echo "AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}" >> .env.production

      - name: Deploy with secrets
        uses: vercel/action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: "--prod"
          working-directory: ./
```

## 质量门禁

### 1. 代码质量检查

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint
        continue-on-error: false

      - name: Run Prettier check
        run: npx prettier --check .
        continue-on-error: false

      - name: Run type checking
        run: npm run type-check
        continue-on-error: false

      - name: Run security audit
        run: npm audit --audit-level=moderate
        continue-on-error: false

      - name: Check test coverage
        run: |
          npm run test:coverage
          COVERAGE=$(node -e "console.log(require('./coverage/coverage-summary.json').total.lines.pct)")
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage too low: $COVERAGE%"
            exit 1
          fi
        continue-on-error: false

  dependency-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Dependabot
        uses: dependabot/fetch-metadata@v2
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"

      - name: Check for vulnerabilities
        run: npm audit --audit-level=moderate
        continue-on-error: false

  performance-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build
        env:
          NODE_ENV: production

      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v10
        with:
          uploadToken: ${{ secrets.LIGHTHOUSE_TOKEN }}
          configPath: "./lighthouse.config.js"
```

### 2. 合并检查

```yaml
# .github/workflows/pr-check.yml
name: Pull Request Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check-branch:
    runs-on: ubuntu-latest
    outputs:
      is-valid: ${{ steps.check.outputs.is-valid }}

    steps:
      - name: Check branch naming
        id: check
        run: |
          BRANCH_NAME="${{ github.head_ref }}"
          if [[ $BRANCH_NAME =~ ^(feature|bugfix|hotfix)/[a-z0-9-]+$ ]]; then
            echo "is-valid=true" >> $GITHUB_OUTPUT
          else
            echo "is-valid=false" >> $GITHUB_OUTPUT
            echo "Branch name should follow pattern: (feature|bugfix|hotfix)/name"
          fi

  conventional-commits:
    runs-on: ubuntu-latest
    if: needs.check-branch.outputs.is-valid == 'true'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check commit messages
        uses: wagoid/commitlint-github-action@v5
        with:
          configFile: ".commitlintrc.json"

  size-check:
    runs-on: ubuntu-latest
    if: needs.check-branch.outputs.is-valid == 'true'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check PR size
        uses: actions/github-script@v7
        with:
          script: |
            const result = await github.rest.pulls.listFiles({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              per_page: 100
            })

            const pr = result.data.find(p => p.number === context.issue.number)
            if (pr && pr.changed_files > 20) {
              core.setFailed('PR is too large. Please split into smaller PRs.')
            }

  comment-on-pr:
    runs-on: ubuntu-latest
    if: always()
    needs: [check-branch, conventional-commits, size-check]

    steps:
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const comments = []

            if (needs.check-branch.outputs.is-valid === 'false') {
              comments.push('❌ Branch name should follow pattern: `(feature|bugfix|hotfix)/name`')
            }

            if (needs.conventional-commits.result === 'failure') {
              comments.push('❌ Commit messages should follow Conventional Commits format')
            }

            if (needs.size-check.result === 'failure') {
              comments.push('❌ PR is too large. Please split into smaller PRs.')
            }

            if (comments.length > 0) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: comments.join('\n')
              })
            }
```

## 监控和通知

### 1. 部署通知

```yaml
# .github/workflows/notifications.yml
name: Deployment Notifications

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types: [completed]
    branches: [main]

jobs:
  notify:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - name: Send Slack notification
        uses: 8398a7/action-slack@v3
        with:
          status: success
          fields: repo,message,commit,author,action,eventName,ref,workflow
          text: "🚀 Deployment to production completed successfully!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Send email notification
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: "Deployment Successful - ${{ github.repository }}"
          body: |
            Deployment to production completed successfully!

            Repository: ${{ github.repository }}
            Commit: ${{ github.sha }}
            Branch: ${{ github.ref }}

            View changes: https://github.com/${{ github.repository }}/commit/${{ github.sha }}
          to: ${{ secrets.NOTIFICATION_EMAIL }}
          from: ${{ secrets.EMAIL_FROM }}

      - name: Create GitHub release
        uses: actions/create-release@v1
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
          body: |
            Changes in this Release
            - Automated deployment from CI/CD pipeline
            - Version: v${{ github.run_number }}
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. 失败通知

```yaml
# .github/workflows/failure-alerts.yml
name: Failure Alerts

on:
  workflow_run:
    workflows: ["CI Pipeline", "Docker Build and Deploy"]
    types: [completed]
    branches: [main]

jobs:
  alert-on-failure:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}

    steps:
      - name: Get workflow run details
        uses: actions/github-script@v7
        id: workflow-details
        with:
          script: |
            const workflow_run = await github.rest.actions.getWorkflowRun({
              owner: context.repo.owner,
              repo: context.repo.repo,
              run_id: ${{ github.event.workflow_run.id }}
            })

            const jobs = await github.rest.actions.listJobsForWorkflowRun({
              owner: context.repo.owner,
              repo: context.repo.repo,
              run_id: ${{ github.event.workflow_run.id }}
            })

            const failedJobs = jobs.data.jobs.filter(job => job.conclusion === 'failure')

            core.setOutput('workflow_name', workflow_run.data.name)
            core.setOutput('failed_jobs', failedJobs.length)
            core.setOutput('run_url', workflow_run.data.html_url)

      - name: Send failure notification
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          fields: repo,message,commit,author,action,eventName,ref,workflow
          text: |
            🚨 Workflow Failed: ${{ steps.workflow-details.outputs.workflow_name }}

            Failed Jobs: ${{ steps.workflow-details.outputs.failed_jobs }}
            Run URL: ${{ steps.workflow-details.outputs.run_url }}

            Please check the logs and fix the issues.
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Create GitHub issue
        uses: actions/github-script@v7
        with:
          script: |
            const title = `🚨 CI/CD Failure: ${{ steps.workflow-details.outputs.workflow_name }}`
            const body = `
            ## Workflow Failure

            **Workflow**: ${{ steps.workflow-details.outputs.workflow_name }}
            **Failed Jobs**: ${{ steps.workflow-details.outputs.failed_jobs }}
            **Run URL**: ${{ steps.workflow-details.outputs.run_url }}
            **Commit**: ${{ github.sha }}
            **Branch**: ${{ github.ref }}

            ### Next Steps
            1. Check the workflow logs
            2. Identify the root cause
            3. Fix the issue
            4. Close this issue

            ---
            *Automatically created by CI/CD pipeline*
            `

            const issue = await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title,
              body,
              labels: ['bug', 'ci-cd', 'urgent']
            })

            core.setOutput('issue_url', issue.data.html_url)
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 自动化运维

### 1. 数据库迁移

```yaml
# .github/workflows/database-migration.yml
name: Database Migration

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      migration:
        description: 'Migration file to run'
        required: true
        type: string

jobs:
  migrate:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup environment
        run: |
          if [[ "${{ github.event.inputs.environment }}" == "production" ]]; then
            echo "DB_HOST=${{ secrets.PROD_DB_HOST }}" >> $GITHUB_ENV
            echo "DB_NAME=${{ secrets.PROD_DB_NAME }}" >> $GITHUB_ENV
            echo "DB_USER=${{ secrets.PROD_DB_USER }}" >> $GITHUB_ENV
            echo "DB_PASSWORD=${{ secrets.PROD_DB_PASSWORD }}" >> $GITHUB_ENV
          else
            echo "DB_HOST=${{ secrets.STAGING_DB_HOST }}" >> $GITHUB_ENV
            echo "DB_NAME=${{ secrets.STAGING_DB_NAME }}" >> $GITHUB_ENV
            echo "DB_USER=${{ secrets.STAGING_DB_USER }}" >> $GITHUB_ENV
            echo "DB_PASSWORD=${{ secrets.STAGING_DB_PASSWORD }}" >> $GITHUB_ENV
          fi

      - name: Run database migration
        run: |
          # 运行迁移脚本
          docker run --rm \
            -v $(pwd)/migrations:/migrations \
            -e PGPASSWORD="${{ env.DB_PASSWORD }}" \
            postgres:15 \
            psql -h "${{ env.DB_HOST }}" -U "${{ env.DB_USER }}" -d "${{ env.DB_NAME }}" -f "/migrations/${{ github.event.inputs.migration }}"

      - name: Verify migration
        run: |
          # 验证迁移结果
          docker run --rm \
            -e PGPASSWORD="${{ env.DB_PASSWORD }}" \
            postgres:15 \
            psql -h "${{ env.DB_HOST }}" -U "${{ env.DB_USER }}" -d "${{ env.DB_NAME }}" -c "SELECT version();"

      - name: Notify completion
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "✅ Database migration completed on ${{ github.event.inputs.environment }} environment"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. 备份自动化

```yaml
# .github/workflows/backup.yml
name: Automated Backup

on:
  schedule:
    - cron: "0 2 * * *"  # 每天凌晨2点
  workflow_dispatch:

jobs:
  backup-database:
    runs-on: ubuntu-latest

    steps:
      - name: Create database backup
        run: |
          TIMESTAMP=$(date +%Y%m%d_%H%M%S)
          BACKUP_FILE="backup_${TIMESTAMP}.sql"

          docker exec db pg_dump -U postgres myapp > "${BACKUP_FILE}"
          gzip "${BACKUP_FILE}"

          # 上传到S3
          aws s3 cp "${BACKUP_FILE}.gz" "s3://${{ secrets.S3_BUCKET }}/backups/db/"

          # 清理本地文件
          rm -f "${BACKUP_FILE}.gz"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          S3_BUCKET: ${{ secrets.S3_BUCKET }}

  backup-files:
    runs-on: ubuntu-latest

    steps:
      - name: Create file backup
        run: |
          TIMESTAMP=$(date +%Y%m%d_%H%M%S)
          BACKUP_FILE="backup_${TIMESTAMP}.tar.gz"

          # 备份静态文件
          tar -czf "${BACKUP_FILE}" -C /app/public .

          # 上传到S3
          aws s3 cp "${BACKUP_FILE}" "s3://${{ secrets.S3_BUCKET }}/backups/files/"

          # 清理本地文件
          rm -f "${BACKUP_FILE}"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          S3_BUCKET: ${{ secrets.S3_BUCKET }}

  cleanup-old-backups:
    runs-on: ubuntu-latest
    needs: [backup-database, backup-files]

    steps:
      - name: Clean old backups
        run: |
          # 删除7天前的备份
          aws s3 ls "s3://${{ secrets.S3_BUCKET }}/backups/db/" | while read -r line; do
            createDate=$(echo $line | awk '{print $1" "$2}')
            createDate=$(date -d "$createDate" +%s)
            olderThan=$(date -d "7 days ago" +%s)
            if [[ $createDate -lt $olderThan ]]; then
              fileName=$(echo $line | awk '{print $4}')
              echo "Deleting old backup: $fileName"
              aws s3 rm "s3://${{ secrets.S3_BUCKET }}/backups/db/$fileName"
            fi
          done
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          S3_BUCKET: ${{ secrets.S3_BUCKET }}
```

## 最佳实践

### 1. CI/CD清单

```markdown
## CI/CD检查清单

### 基础配置
- [ ] 设置合适的事件触发器
- [ ] 配置环境变量和密钥
- [ ] 设置缓存策略
- [ ] 配置并发执行

### 测试阶段
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] E2E测试通过
- [ ] 安全扫描通过

### 构建阶段
- [ ] 代码编译成功
- [ ] 优化构建产物
- [ ] 构建镜像正确
- [ ] 生成构建报告

### 部署阶段
- [ ] 环境准备就绪
- [ ] 部署策略配置
- [ ] 健康检查通过
- [ ] 回滚机制就绪

### 监控和通知
- [ ] 部署状态通知
- [ ] 错误报警配置
- [ ] 性能监控
- [ ] 日志收集配置
```

### 2. 安全检查清单

```markdown
## CI/CD安全检查清单

### 密钥管理
- [ ] 使用环境变量存储密钥
- [ ] 定期轮换密钥
- [ ] 限制密钥访问权限
- [ ] 避免在日志中输出密钥

### 代码安全
- [ ] 依赖项安全扫描
- [ ] 代码漏洞扫描
- [ ] SAST/DAST检查
- [ ] 容器镜像安全扫描

### 网络安全
- [ ] 使用HTTPS传输
- [ ] 网络访问控制
- [ ] 防火墙配置
- [ ] VPN/专线连接

### 操作安全
- [ ] 最小权限原则
- [ ] 审计日志记录
- [ ] 变更管理流程
- [ ] 应急响应预案
```

## 总结

通过本指南，我们学习了Next.js项目的CI/CD流水线配置：

### 核心概念
- CI/CD的基本原理和价值
- 自动化测试和部署的重要性
- DevOps文化的实践

### 实践技能
- GitHub Actions配置
- GitLab CI设置
- 环境管理策略
- 质量门禁配置

### 高级主题
- 自动化运维
- 监控和通知
- 安全最佳实践
- 故障处理流程

### 从PHP开发者角度
- 从手动部署到自动化部署的转变
- CI/CD如何提升开发效率和代码质量
- 现代DevOps工具的优势

掌握CI/CD技能，将帮助您建立高效的开发流程，提高代码质量，加速产品交付，为团队带来更高的生产力和更好的协作体验。CI/CD不仅是工具的使用，更是现代软件开发文化的体现。