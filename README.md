# PHP Security RSS

Generador automático de un feed RSS con los avisos oficiales de seguridad de PHP publicados en el repositorio `php/php-src` de GitHub.

Feed: https://carlosdaairaevelb.github.io/php-security-rss/feed.xml

## Funcionamiento

1. GitHub Actions ejecuta el workflow `update-rss.yml` cada 12 horas (06:17 y 18:17 UTC) o manualmente desde la pestaña *Actions*.
2. `generate_rss.py` consulta la API de GitHub Security Advisories y genera `docs/feed.xml` con los 30 avisos más recientes.
3. El feed se publica en GitHub Pages, junto con `status.xml`, que guarda la hora de la última generación correcta.
4. Un flujo de Power Automate lee el feed y publica los avisos nuevos en un canal de Microsoft Teams.
5. Otro flujo, «PHP RSS - Vigilante», lee `status.xml` cada 6 horas y avisa en el mismo canal si lleva más de 26 horas sin actualizarse.

## Contenido de cada aviso

- **Título:** gravedad entre corchetes y resumen, por ejemplo `[CRÍTICA] PHP-FPM request smuggling…`.
- **Descripción:** gravedad, puntuación CVSS, CVE, componente afectado, versiones corregidas y un resumen del aviso.
- **Categorías:** gravedad (`critical`, `high`, `medium`, `low`) y componente (`sapi-fpm`, `ext-session`…), útiles para filtrar en Power Automate.
- **Enlace:** el aviso completo en GitHub.

## Mantenimiento

- GitHub desactiva los workflows programados de repositorios públicos tras 60 días sin actividad. El job `keepalive` reactiva el workflow en cada ejecución programada para evitarlo.
- Si el workflow falla, se desactiva o GitHub Pages no responde, `status.xml` deja de actualizarse y el vigilante lo avisa en Teams tras dos ejecuciones perdidas (más de 26 horas).
- El número de avisos y la longitud del resumen se ajustan con `MAX_ITEMS` y `SUMMARY_MAX_CHARS` en `generate_rss.py`.

## Tecnologías

- Python 3 (solo biblioteca estándar)
- GitHub Actions
- GitHub Pages
- GitHub Security Advisories API
- RSS 2.0
- Microsoft Power Automate y Teams

## Objetivo

Centralizar y automatizar las notificaciones de vulnerabilidades y actualizaciones de seguridad de PHP, sin necesidad de conectores Premium de Power Automate.
