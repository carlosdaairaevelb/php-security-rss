# PHP Security RSS

Generador automático de un feed RSS con los avisos oficiales de seguridad de PHP publicados en el repositorio `php/php-src` de GitHub.

## Funcionamiento

1. Consulta la API pública de GitHub para obtener los avisos de seguridad de PHP.
2. Genera un archivo RSS (`feed.xml`) mediante Python.
3. Actualiza y publica el feed automáticamente mediante GitLab CI/CD y GitLab Pages.
4. Permite integrar las alertas en Microsoft Teams mediante Power Automate.

## Tecnologías

- Python 3
- GitLab CI/CD
- GitLab Pages
- GitHub Security Advisories API
- RSS 2.0

## Objetivo

Centralizar y automatizar las notificaciones de vulnerabilidades y actualizaciones de seguridad de PHP, sin necesidad de conectores Premium de Power Automate.
