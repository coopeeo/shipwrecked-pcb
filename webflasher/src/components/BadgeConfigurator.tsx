import { useEffect, useState } from "react";
import { useMicroPython } from "../MicroPythonContext";
import semver from "semver";

interface ConfigurationAttrs {
    // all of these are synchronized with the device
    userName: string;
    userHandle: string;
    userPronouns: string;
}

export default function BadgeConfigurator() {
    const { isConnected, mp } = useMicroPython();
    const [config, setConfig] = useState<ConfigurationAttrs>({
        userName: "",
        userPronouns: "",
        userHandle: "",
    });
    const [status, setStatus] = useState<string>("");
    const [firmware, setFirmware] = useState<{ files: { path: string, content: string }[], folders: string[] } | 'NOTFETCHED' | 'UPTODATE'>('NOTFETCHED');

    useEffect(() => {

        (async () => {
            if (isConnected && mp) {
                const files: any[] = await mp.listFiles();
                console.log("Files on device:", files);
                if (files.find(file => file.path === "/config.json")) {
                    const data = await mp.downloadFileToString("/config.json");
                    console.log("Config data:", data);
                    try {
                        const parsedConfig = JSON.parse(data) as ConfigurationAttrs;
                        setConfig(parsedConfig);
                    } catch (error) {
                        console.error("Failed to parse config.json:", error);
                    }
                } else {
                    console.warn("config.json not found on the device.");
                }
                if (firmware === 'NOTFETCHED') {
                    setStatus("Fetching firmware version...");
                    const versionResponse = await fetch("https://api.github.com/repos/mpkendall/shipwrecked-pcb/contents/Code/VERSION?ref=deploy");
                    const versionData = await versionResponse.json();
                    const latestVersion = atob(versionData.content);
                    console.log("Latest firmware version:", latestVersion);
                    
                    // get the version on the device
                    setStatus("Checking device firmware version...");
                    const deviceVersion = await mp.downloadFileToString("/VERSION");
                    console.log("Device firmware version:", deviceVersion);
                    if (semver.valid(deviceVersion) && !semver.lt(deviceVersion, latestVersion)) {
                        setStatus("Device firmware is up to date.");
                        setFirmware('UPTODATE'); // no firmware update needed
                    } else {
                        setStatus("Fetching firmware update...");
                        const repoTree = await fetch("https://api.github.com/repos/mpkendall/shipwrecked-pcb/git/trees/deploy?recursive=1");
                        const treeData = await repoTree.json();
                        const firmwareFiles = treeData.tree.filter((file: any) => file.path.startsWith("Code/") && file.path);
                        const firmwareFolders = firmwareFiles.filter((file: any) => file.type === "tree").map((folder: any) => folder.path);
                        const firmwareFilesData = await Promise.all(firmwareFiles.filter((file: any) => file.type === "blob").map(async (file: any) => {
                            const filePath = file.path.replace("Code/", "/");
                            const fileResponse = await fetch(`https://api.github.com/repos/mpkendall/shipwrecked-pcb/contents/${file.path}?ref=deploy`);
                            const fileData = await fileResponse.json();
                            const decodedContent = atob(fileData.content.replace(/\n/g, ''));
                            const content = new Uint8Array(decodedContent.split('').map(c => c.charCodeAt(0)));
                            return { path: filePath, content };
                        }));
                        console.log("Folders:", firmwareFolders);
                        console.log("Firmware files:", firmwareFilesData.map(f => f.path));
                        setFirmware({ files: firmwareFilesData, folders: firmwareFolders });
                        setStatus("Firmware update available.");
                    }
                }
            }
        })();
    }, [isConnected, mp, firmware]);

    function handleSave(): void {
        if (isConnected && mp) {
            const configData = JSON.stringify(config, null, 2);
            console.log("Saving configuration:", configData);
            setStatus("Saving configuration...");
            mp.uploadFileFromString("/config.json", configData)
                .then(() => {
                    console.log("Configuration saved successfully.");
                    setStatus("Configuration saved successfully.");
                })
                .catch((error) => {
                    console.error("Failed to save configuration:", error);
                    setStatus("Failed to save configuration.");
                });
        } else {
            console.warn("Not connected to the device.");
        }
    }

    function handleUploadFirmware(): void {
        (async () => {
        if (isConnected && mp && firmware !== 'UPTODATE' && firmware !== 'NOTFETCHED') {
            setStatus("Uploading firmware...");
            // first, create the folders
            // we can't do this in parallel unfortunately
            for (const folder of firmware.folders) {
                console.log("Creating folder:", folder);
                setStatus(`Creating folder: ${folder}`);
                await mp.createFolder(folder);
            }
            // then upload the files
            for (const file of firmware.files) {
                console.log("Uploading file:", file.path);
                setStatus(`Uploading file: ${file.path}`);
                await mp.uploadFile(file.path, file.content);
            }
            setStatus("Firmware uploaded successfully.");
            setFirmware('UPTODATE'); // mark as up to date after upload
        }
    })();
    }

    const fields = (
        <div>
        <div>
                <label>
                    Your Name:
                    <input
                        type="text"
                        value={config.userName}
                        disabled={!isConnected}
                        onChange={(e) => setConfig({ ...config, userName: e.target.value })}
                    />
                </label>
            </div>
            <div>
                <label>
                    Pronouns:
                    <input
                        type="text"
                        value={config.userPronouns}
                        disabled={!isConnected}
                        onChange={(e) => setConfig({ ...config, userPronouns: e.target.value })}
                    />
                </label>
            </div>
            <div>
                <label>
                    Slack Handle: @
                    <input
                        type="text"
                        value={config.userHandle}
                        disabled={!isConnected}
                        onChange={(e) => setConfig({ ...config, userHandle: e.target.value })}
                    />
                </label>
            </div>

            <div>
                <button onClick={handleSave}>Save To Badge</button>
            </div>
            </div>
    )

    const firmwareUpdate = (
        <div>
            <h3>Firmware Update</h3>
            <button onClick={handleUploadFirmware}>Upload Firmware</button>
        </div>
    );

    return (
        <div>
            <h2>Badge Configurator</h2>
            <p>Status: {status}</p>
            {isConnected && firmware === 'UPTODATE' ? fields : firmwareUpdate}
        </div>
    );
}