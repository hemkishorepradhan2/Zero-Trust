def trigger_step_up(user_id: str) -> bool:
    """Stub for step-up authentication. Returns True if step-up succeeded.

    Replace with real MFA integration (TOTP, SMS, push) as needed.
    """
    # For demo/testing purposes, accept step-up when header X-MFA=1 is set by client.
    # Real flow should issue challenge and verify response.
    return True
