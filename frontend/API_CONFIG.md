# API Configuration Guide

## Overview
Frontend tự động detect API URL dựa trên môi trường chạy.

## Cấu hình cho Development (Local)

1. Copy file `.env.example` thành `.env.local`:
```bash
cd frontend
cp .env.example .env.local
```

2. Chỉnh sửa `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Chạy development server:
```bash
npm run dev
```

## Cấu hình cho Production (Server)

### Cách 1: Sử dụng biến môi trường

1. Tạo file `.env.production`:
```env
# Thay YOUR_SERVER_IP bằng IP thực tế của server
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000/api
```

Ví dụ:
```env
NEXT_PUBLIC_API_URL=http://192.168.1.43:8000/api
```

Hoặc sử dụng domain:
```env
NEXT_PUBLIC_API_URL=https://api.logicguard.com/api
```

2. Build và deploy:
```bash
npm run build
npm run start
```

### Cách 2: Auto-detect (Không cần cấu hình)

Nếu không set `NEXT_PUBLIC_API_URL`, hệ thống tự động detect:

- **Local**: `http://localhost:8000/api`
- **Server IP**: `http://<current-ip>:8000/api`

Ví dụ: Nếu truy cập qua `http://192.168.1.43:3000`, API sẽ tự động là `http://192.168.1.43:8000/api`

## Docker Deployment

### docker-compose.yml example:

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://192.168.1.43:8000/api
      # Hoặc để trống để auto-detect
      # - NEXT_PUBLIC_API_URL=
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
```

## Testing

Test API connection:
```bash
# Check API URL trong browser console
console.log(window.location.hostname)

# Test API endpoint
curl http://YOUR_SERVER_IP:8000/api/health
```

## Troubleshooting

### Frontend không kết nối được backend

1. Kiểm tra IP có đúng không:
```bash
# Trên server
hostname -I
```

2. Kiểm tra port 8000 có mở không:
```bash
sudo netstat -tulpn | grep 8000
```

3. Kiểm tra firewall:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

4. Kiểm tra CORS settings trong backend (FastAPI):
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production, specify IP/domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend build error

Nếu gặp lỗi `Cannot find name 'process'`:
```bash
cd frontend
npm install --save-dev @types/node
```

## Production Checklist

- [ ] Set `NEXT_PUBLIC_API_URL` trong `.env.production`
- [ ] Backend CORS cho phép frontend origin
- [ ] Firewall mở port 8000 (backend) và 3000 (frontend)
- [ ] Test từ browser trên máy khác trong cùng network
- [ ] SSL/HTTPS cho production (optional but recommended)

## Multiple Environments

Tạo nhiều env files:

- `.env.local` - Development trên máy local
- `.env.production` - Production server
- `.env.staging` - Staging server (optional)

Switch environment:
```bash
# Development
npm run dev

# Production
npm run build
npm run start

# With specific env file
npm run build -- --env production
```
