# EduPath AI — 1-Click GitHub Actions Workflow Activator
# This script refreshes GitHub CLI scopes to include 'workflow',
# unignores .github/, and pushes all 9 CI/CD workflows to GitHub.

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "EDUPATH AI - GITHUB ACTIONS WORKFLOW ACTIVATOR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Step 1: Requesting GitHub CLI 'workflow' authorization scope..." -ForegroundColor Yellow
Write-Host "A browser window will open. Click 'Authorize' to grant the workflow permission." -ForegroundColor Yellow
gh auth refresh -s workflow

Write-Host "`nStep 2: Activating .github/ directory in git..." -ForegroundColor Green
(Get-Content .gitignore) | Where-Object { $_ -notmatch '^\.github/' -and $_ -notmatch 'GitHub Workflows local' } | Set-Content .gitignore

Write-Host "Step 3: Staging .github/workflows and committing..." -ForegroundColor Green
git add .github/ .gitignore
git commit -m "ci: activate .github/workflows on GitHub Actions"

Write-Host "Step 4: Pushing workflows to GitHub remotes..." -ForegroundColor Green
git push origin master
git push origin master:main
git push origin master:upgrade/production-release

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] GitHub Actions workflows successfully activated!" -ForegroundColor Green
Write-Host "View live pipeline runs at: https://github.com/hasinimaha2008/EduPath-AI-/actions" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
