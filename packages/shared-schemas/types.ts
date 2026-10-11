export type RunStatus = 'CREATED' | 'QUEUED' | 'PREPARING' | 'RUNNING' | 'SCORING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'BLOCKED';
export type SecurityStatus = 'PASSED' | 'FAILED' | 'INCONCLUSIVE' | 'NOT_APPLICABLE' | 'NOT_RUN';
export type ReleaseOutcome = 'PASS' | 'FAIL' | 'INCONCLUSIVE';
export type Role = 'owner' | 'admin' | 'developer' | 'viewer';
