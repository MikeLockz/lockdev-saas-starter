import { useState } from 'react';
import { useMFA } from '@/hooks/useMFA';
import { useUserProfile } from '@/hooks/useUserProfile';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

type SetupStep = 'idle' | 'scanning' | 'verifying' | 'complete';

export function MFASetup() {
    const { profile } = useUserProfile();
    const { setupMFA, verifyMFA, disableMFA } = useMFA();
    const [step, setStep] = useState<SetupStep>('idle');
    const [secret, setSecret] = useState<string>('');
    const [code, setCode] = useState('');
    const [backupCodes, setBackupCodes] = useState<string[]>([]);
    const [disablePassword, setDisablePassword] = useState('');
    const [showDisable, setShowDisable] = useState(false);

    const handleSetup = async () => {
        try {
            const result = await setupMFA.mutateAsync();
            setSecret(result.secret);
            setStep('scanning');
        } catch (error) {
            console.error('MFA setup failed:', error);
        }
    };

    const handleVerify = async () => {
        try {
            const result = await verifyMFA.mutateAsync({ code });
            setBackupCodes(result.backup_codes);
            setStep('complete');
        } catch (error) {
            console.error('MFA verification failed:', error);
        }
    };

    const handleDisable = async () => {
        try {
            await disableMFA.mutateAsync({ password: disablePassword });
            setShowDisable(false);
            setDisablePassword('');
        } catch (error) {
            console.error('MFA disable failed:', error);
        }
    };

    // MFA already enabled
    if (profile?.mfa_enabled && step === 'idle') {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        Two-Factor Authentication
                        <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                            Enabled
                        </span>
                    </CardTitle>
                    <CardDescription>
                        Your account is protected with two-factor authentication
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Two-factor authentication adds an extra layer of security to your account.
                        You'll need to enter a code from your authenticator app when signing in.
                    </p>

                    {showDisable ? (
                        <div className="space-y-4 p-4 border rounded-lg">
                            <p className="text-sm font-medium text-destructive">
                                Disabling MFA will make your account less secure
                            </p>
                            <div className="space-y-2">
                                <Label htmlFor="disablePassword">Enter your password to confirm</Label>
                                <Input
                                    id="disablePassword"
                                    type="password"
                                    value={disablePassword}
                                    onChange={(e) => setDisablePassword(e.target.value)}
                                    placeholder="Password"
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    variant="destructive"
                                    onClick={handleDisable}
                                    disabled={!disablePassword || disableMFA.isPending}
                                >
                                    {disableMFA.isPending ? 'Disabling...' : 'Disable MFA'}
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => {
                                        setShowDisable(false);
                                        setDisablePassword('');
                                    }}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <Button
                            variant="outline"
                            onClick={() => setShowDisable(true)}
                            className="text-destructive"
                        >
                            Disable Two-Factor Authentication
                        </Button>
                    )}
                </CardContent>
            </Card>
        );
    }

    // Setup flow
    return (
        <Card>
            <CardHeader>
                <CardTitle>Two-Factor Authentication</CardTitle>
                <CardDescription>
                    Add an extra layer of security to your account
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                {step === 'idle' && (
                    <>
                        <p className="text-sm text-muted-foreground">
                            Two-factor authentication adds an extra layer of security by requiring
                            a code from your phone in addition to your password.
                        </p>
                        <Button onClick={handleSetup} disabled={setupMFA.isPending}>
                            {setupMFA.isPending ? 'Setting up...' : 'Set Up Two-Factor Authentication'}
                        </Button>
                    </>
                )}

                {step === 'scanning' && (
                    <div className="space-y-4">
                        <div className="p-4 rounded-lg border bg-muted/50">
                            <p className="font-medium mb-2">Step 1: Scan the QR code</p>
                            <p className="text-sm text-muted-foreground mb-4">
                                Use your authenticator app (Google Authenticator, Authy, etc.) to scan:
                            </p>

                            {/* QR code placeholder - in production you would generate a QR code */}
                            <div className="flex justify-center p-4 bg-white rounded-lg mb-4">
                                <div className="text-center">
                                    <p className="text-xs text-gray-500 mb-2">Can't scan? Enter manually:</p>
                                    <code className="text-xs break-all bg-gray-100 p-2 rounded block max-w-xs">
                                        {secret}
                                    </code>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 rounded-lg border bg-muted/50">
                            <p className="font-medium mb-2">Step 2: Enter verification code</p>
                            <div className="space-y-2">
                                <Label htmlFor="verifyCode">6-digit code from your app</Label>
                                <Input
                                    id="verifyCode"
                                    value={code}
                                    onChange={(e) => setCode(e.target.value)}
                                    placeholder="000000"
                                    maxLength={6}
                                    className="text-center text-2xl tracking-widest"
                                />
                            </div>
                            <div className="flex gap-2 mt-4">
                                <Button
                                    onClick={handleVerify}
                                    disabled={code.length !== 6 || verifyMFA.isPending}
                                >
                                    {verifyMFA.isPending ? 'Verifying...' : 'Verify and Enable'}
                                </Button>
                                <Button variant="outline" onClick={() => setStep('idle')}>
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {step === 'complete' && (
                    <div className="space-y-4">
                        <div className="p-4 rounded-lg border border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800">
                            <p className="font-medium text-green-800 dark:text-green-300">
                                ✓ Two-factor authentication enabled!
                            </p>
                        </div>

                        <div className="p-4 rounded-lg border bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
                            <p className="font-medium text-yellow-800 dark:text-yellow-300 mb-2">
                                ⚠️ Save your backup codes
                            </p>
                            <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-4">
                                These codes can be used if you lose access to your authenticator app.
                                Each code can only be used once.
                            </p>
                            <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                                {backupCodes.map((code, i) => (
                                    <div key={i} className="px-3 py-2 bg-white dark:bg-gray-900 rounded border">
                                        {code}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <Button onClick={() => setStep('idle')}>Done</Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
