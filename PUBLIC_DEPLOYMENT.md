# Public multi-user deployment — separate future work

This local guest prototype is not production-ready and has not been publicly deployed.

Before public access:
- Implement authentication, authorisation and per-user ownership checks on every record, file, export and deletion.
- Test cross-user isolation, ID enumeration, privilege boundaries and concurrent operations.
- Add HTTPS, secure sessions, CSRF protection appropriate to the deployment, rate limits and abuse controls.
- Keep Ollama private; configure backend-to-inference networking explicitly. Hosted localhost is not the owner's laptop.
- Add resource-isolated PDF parsing with hard memory/CPU limits, upload quotas and a reviewed threat model.
- Load-test GPU queues, timeouts, cancellation, admission control and multi-worker coordination.
- Establish privacy notices, retention rules, export/deletion operations, incident handling and secure backups.
- Obtain educational content review and source permissions; evaluate Hindi/Hinglish and correct alternative solutions.
- Add reproducible dependency/security checks and operational monitoring without logging private answer text.
- Review accessibility with keyboard, screen readers, zoom and multiple real mobile devices.
- Document model licence obligations, attribution and realistic product claims.

No paid infrastructure, authentication provider, cloud AI, analytics or remote logging is activated by this project.
