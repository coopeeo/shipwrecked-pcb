import { useMicroPython } from "../../MicroPythonContext";

export interface AppManifest {
    displayName: string;
    logoPath: string;
    appNumber: number;
}

export interface App {
    manifest: AppManifest;
    path: string;
}

interface AppListItemProps {
    app: App;
    onDelete: (app: App) => void;
}

export default function AppListItem({ app, onDelete }: AppListItemProps) {
    const { manifest, path } = app;

    const handleDelete = () => {
        const confirmDelete = window.confirm(`Are you sure you want to delete ${manifest.displayName}?`);
        if (confirmDelete) {
            onDelete(app);
        }
    };

    return (
        <div className="app-list-item">
            <div className="app-info">
                <h3>{manifest.displayName}</h3>
                <p>App #{manifest.appNumber}</p>
                <p>Logo: {manifest.logoPath}</p>
                <p>Path: {path}</p>
            </div>
            <div className="app-actions">
                <button onClick={handleDelete}>Delete</button>
            </div>
        </div>
    );
}
