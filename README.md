# Health Appointment System

## Git Workflow

This project follows the GitFlow branching model:

- `master`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches (e.g., feature/user-authentication)
- `release/*`: Preparing for a new production release
- `hotfix/*`: Quick fixes for the production version

### Development Workflow:

1. Create a feature branch from `develop`: `git checkout -b feature/your-feature-name develop`
2. Work on your feature and commit changes
3. Push your feature branch to GitHub: `git push -u origin feature/your-feature-name`
4. Create a pull request to merge into `develop`
5. After review, merge the feature into `develop`

When ready for release, a release branch will be created from `develop` and eventually merged into both `master` and back into `develop`.

┌─────────────────────────────────────────────────┐
│                Kubernetes Cluster               │
│                                                 │
│  ┌──────────┐    ┌─────────┐    ┌─────────────┐ │
│  │ Frontend │    │ Backend │    │  Database   │ │
│  │ Service  │━━━━│ Service │━━━━│ StatefulSet │ │
│  │(React.js)│    │(Django) │    │(PostgreSQL) │ │
│  └──────────┘    └─────────┘    └─────────────┘ │
│                                                 │
│  ┌─────────────┐  ┌──────────┐  ┌───────────┐   │
│  │  Ingress    │  │ Secrets  │  │   HPA     │   │
│  │ Controller  │  │ Manager  │  │           │   │
│  └─────────────┘  └──────────┘  └───────────┘   │
└─────────────────────────────────────────────────┘