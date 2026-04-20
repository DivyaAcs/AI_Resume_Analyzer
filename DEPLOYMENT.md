# Deployment Guide - AI Resume Analyzer

## Quick Start (No Docker Required)

The application is already running on your local machine!

### Access the Application
- **Local URL**: http://localhost:5000
- **Network URL**: http://192.168.0.104:5000

### Stop the Application
Press `Ctrl+C` in the terminal where the app is running.

---

## Docker Deployment (Optional)

### Prerequisites
- Docker Desktop for Windows
- OR Docker with WSL2

### Installation Steps

#### Option 1: Docker Desktop (Recommended)
1. **Download**: https://www.docker.com/products/docker-desktop/
2. **Install**: Run the installer and follow setup wizard
3. **Restart**: Restart your computer
4. **Verify**: Open PowerShell and run `docker --version`

#### Option 2: WSL2 (Windows 10/11 Pro)
```powershell
# Install WSL
wsl --install

# Install Docker inside WSL
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Running with Docker

Once Docker is installed:

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d

# Stop the application
docker-compose down
```

### Docker URLs
- **Application**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

---

## Production Deployment

### Environment Variables
Create a `.env` file:
```env
SECRET_KEY=your-production-secret-key-here
MAX_CONTENT_LENGTH=16777216
FLASK_ENV=production
```

### Security Settings
- Set a strong `SECRET_KEY`
- Use HTTPS in production
- Configure firewall rules
- Set up proper logging

### Scaling Options
- **Load Balancer**: Nginx or AWS ALB
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for session management
- **Monitoring**: Prometheus + Grafana

---

## Cloud Deployment Options

### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

### AWS
- Use AWS ECS or Elastic Beanstalk
- Set up RDS for database
- Configure Application Load Balancer
- Use S3 for file storage

### Google Cloud Platform
- Use Cloud Run or App Engine
- Set up Cloud SQL
- Configure Cloud Storage

### Azure
- Use Azure App Service
- Set up Azure SQL Database
- Configure Azure Storage

---

## Troubleshooting

### Common Issues

#### Docker Not Found
```
Error: 'docker' is not recognized
```
**Solution**: Install Docker Desktop from docker.com

#### Port Already in Use
```
Error: Port 5000 is already in use
```
**Solution**: 
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

#### Permission Denied
```
Error: Permission denied
```
**Solution**: Run PowerShell as Administrator

#### Module Not Found
```
Error: ModuleNotFoundError: No module named 'flask'
```
**Solution**: 
```bash
pip install -r requirements.txt
```

### Health Check
Always verify the application is running:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:00:00",
  "version": "1.0.0"
}
```

---

## Performance Optimization

### Database
- Add database for user data storage
- Implement connection pooling
- Use read replicas for scaling

### Caching
- Redis for session storage
- Cache analysis results
- Use CDN for static assets

### Monitoring
- Set up application monitoring
- Track response times
- Monitor error rates

---

## Backup and Recovery

### Data Backup
- Regular database backups
- File storage backups
- Configuration backups

### Disaster Recovery
- Multi-region deployment
- Automated failover
- Recovery procedures

---

## Support

For deployment issues:
1. Check the logs: `logs/resume_analyzer.log`
2. Verify health endpoint: `/health`
3. Check Docker logs: `docker-compose logs`
4. Review this troubleshooting section

---

## Security Considerations

- Never commit sensitive data to version control
- Use environment variables for secrets
- Implement rate limiting
- Validate all user inputs
- Use HTTPS in production
- Regular security updates
