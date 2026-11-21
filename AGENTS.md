# Project guidance for Codex

- Use `docs/Contexto_Proyecto2_Punto4_Web.md` as the primary reference for the project's scientific explanations, conclusions, and website requirements. Read it before implementing or modifying analytical features.
- Before implementing an analytical feature in JavaScript, consult the corresponding original exploration, cleaning, statistical analysis, and visualization scripts in `python/exploracion/`, `python/tratamiento/`, and `python/correlaciones/`. Use them to validate the JavaScript implementation.
- Preserve the original definitions of filters, SAE series, processing groups, statistical methods, and data exclusions. Do not change previously completed scientific analyses without explicit instructions.
- Distinguish statistics that can be recalculated dynamically from results that require verified precomputation. Ensure displayed statistics correspond to the active filters and analyzed observations. Never reuse full-dataset significance values when filters change the analyzed observations.
- Use the existing Python analyses and verified results as scientific references. Never invent statistical results, conclusions, or bibliographic information.
- Preserve the cleaned CSV, its original values, and its column names. Do not modify the Python reference scripts or the cleaned CSV.
- Preserve the mandatory website section order specified in the context document.
- Maintain HTML, CSS, and vanilla JavaScript, with relative paths and compatibility with static GitHub Pages hosting.
- Maintain the white-and-blue visual identity and keep all user-facing website content in Spanish.
- Implement features incrementally and verify their behavior.
