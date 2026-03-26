# Imagen base Nginx
FROM nginx:alpine

# Eliminar configuración por defecto
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf

# Puerto expuesto
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]