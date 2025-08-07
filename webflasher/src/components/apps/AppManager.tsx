import { useState } from 'react';
import { useMicroPython } from '../../MicroPythonContext';
import AppListItem, { App } from './AppListItem';

interface AppManagerProps {
    apps: App[];
    onAppListChange: () => void;
}

export default function AppManager({ apps, onAppListChange }: AppManagerProps) {
    const { mp } = useMicroPython();
    const [status, setStatus] = useState<string>("");

    const handleAppUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!event.target.files || !event.target.files[0] || !mp) return;

        const file = event.target.files[0];
        if (!file.name.endsWith('.zip')) {
            setStatus("Error: Please select a .zip file");
            return;
        }

        try {
            setStatus("Processing app upload...");
            const JSZip = (await import('jszip')).default;
            const zip = new JSZip();
            const zipContent = await zip.loadAsync(file);
            
            // Verify manifest.json exists in the root
            const manifestFile = zipContent.files['manifest.json'];
            if (!manifestFile) {
                setStatus("Error: Invalid app package (missing manifest.json)");
                return;
            }

            // Parse and validate manifest
            const manifestContent = await manifestFile.async('text');
            const manifest = JSON.parse(manifestContent);
            if (!manifest.displayName || !manifest.logoPath || typeof manifest.appNumber !== 'number') {
                setStatus("Error: Invalid manifest.json (missing required fields: displayName, logoPath, or appNumber)");
                return;
            }

            // Create app directory
            const appPath = `/apps/${manifest.displayName.replace(/[^a-zA-Z0-9_\-]/g, '_')}`;
            await mp.createFolder(appPath);

            // Upload all files
            for (const [path, file] of Object.entries(zipContent.files)) {
                if (!file.dir) {
                    const content = await file.async('uint8array');
                    await mp.uploadFile(`${appPath}/${path}`, content);
                }
            }

            setStatus("App uploaded successfully");
            onAppListChange();
        } catch (error) {
            console.error("Failed to upload app:", error);
            setStatus("Failed to upload app");
        }
    };

    const handleAppDelete = async (app: App) => {
        if (!mp) return;

        try {
            setStatus(`Deleting ${app.manifest.displayName}...`);
            await mp.removeFolder(app.path);
            setStatus(`${app.manifest.displayName} deleted successfully`);
            onAppListChange();
        } catch (error) {
            console.error("Failed to delete app:", error);
            setStatus(`Failed to delete ${app.manifest.displayName}`);
        }
    };

    return (
        <div className="app-manager">
            <h3>App Management</h3>
            <p>{status}</p>
            
            <div className="app-upload">
                <input
                    type="file"
                    accept=".zip"
                    onChange={handleAppUpload}
                    style={{ display: 'none' }}
                    id="app-upload-input"
                />
                <button onClick={() => document.getElementById('app-upload-input')?.click()}>
                    Upload New App
                </button>
            </div>

            <div className="app-list">
                {apps.length === 0 ? (
                    <p>No apps installed</p>
                ) : (
                    apps.map(app => (
                        <AppListItem
                            key={app.path}
                            app={app}
                            onDelete={handleAppDelete}
                        />
                    ))
                )}
            </div>
        </div>
    );
}
