# Dockerfile para frontend Vue.js 3
# Solo para desarrollo - Producción usa Nginx del servidor

FROM node:24-alpine

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar el resto del código
COPY . .

# Exponer puerto de Vite dev server
EXPOSE 5173

# Comando de desarrollo con hot reload
# --host 0.0.0.0 permite acceso desde fuera del contenedor
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
