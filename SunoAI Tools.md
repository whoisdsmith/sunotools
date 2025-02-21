# SunoAI Tools

File Path: Sunodownloader/index.html
File Content:

```html
<!doctype html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Suno Music Downloader</title>
</head>

<body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
</body>

</html>
```

File Path: Sunodownloader/README.md
File Content:

```md
# Suno Music downloader

A tauri app to easily download entire Suno playlists in a few clicks


```

File Path: Sunodownloader/src/App.css
File Content:

```css

html, body, #root {
    height: 100vh;
}


/* .logo.vite:hover {
  filter: drop-shadow(0 0 2em #747bff);
}

.logo.react:hover {
  filter: drop-shadow(0 0 2em #61dafb);
}
:root {
  font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;

  color: #0f0f0f;
  background-color: #f6f6f6;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

.container {
  margin: 0;
  padding-top: 10vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: 0.75s;
}

.logo.tauri:hover {
  filter: drop-shadow(0 0 2em #24c8db);
}

.row {
  display: flex;
  justify-content: center;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}

a:hover {
  color: #535bf2;
}

h1 {
  text-align: center;
}

input,
button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  color: #0f0f0f;
  background-color: #ffffff;
  transition: border-color 0.25s;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
}

button {
  cursor: pointer;
}

button:hover {
  border-color: #396cd8;
}
button:active {
  border-color: #396cd8;
  background-color: #e8e8e8;
}

input,
button {
  outline: none;
}

#greet-input {
  margin-right: 5px;
}

@media (prefers-color-scheme: dark) {
  :root {
    color: #f6f6f6;
    background-color: #2f2f2f;
  }

  a:hover {
    color: #24c8db;
  }

  input,
  button {
    color: #ffffff;
    background-color: #0f0f0f98;
  }
  button:active {
    background-color: #0f0f0f69;
  }
} */

```

File Path: Sunodownloader/src/App.tsx
File Content:

```tsx
import "./App.css";

import * as path from "@tauri-apps/api/path"

import { ActionIcon, AppShell, Badge, Box, Button, CloseButton, Divider, FileInput, Flex, Group, Image, NavLink, Paper, Popover, Progress, Stack, Table, Text, TextInput, Title } from "@mantine/core"
import { BaseDirectory, create } from "@tauri-apps/plugin-fs";
import { IconBrandGithub, IconCoffee, IconFolder, IconFolderFilled, IconHelp, IconHelpCircle, IconHelpCircleFilled, IconHelpSmall, IconLink, IconSolarElectricity, IconVinyl } from "@tabler/icons-react";
import Suno, { IPlaylist, IPlaylistClip, IPlaylistClipStatus } from "./services/Suno";
import { addImageToMp3, deletePath, ensureDir, writeFile } from "./services/RustFunctions";
import { delay, getRandomBetween, showError, showSuccess } from "./services/Utils";
import { useEffect, useRef, useState } from "react";

import Footer from "./components/Footer";
import SectionHeading from "./components/SectionHeading";
import StatusIcon from "./components/StatusIcon";
import { exit } from '@tauri-apps/plugin-process'
import { fetch } from "@tauri-apps/plugin-http"
import filenamify from "filenamify"
import { invoke } from "@tauri-apps/api/core";
import { modals } from "@mantine/modals";
import { open as openDialog } from "@tauri-apps/plugin-dialog";
import pLimit from "p-limit"
import reactLogo from "./assets/react.svg";
import scrollIntoView from "scroll-into-view-if-needed"
import { sendNotification } from "@tauri-apps/plugin-notification";

function App() {

    const [playlistUrl, setPlaylistUrl] = useState("")
    const [saveFolder, setSaveFolder] = useState("")
    const [isGettingPlaylist, setIsGettingPLaylist] = useState(false)
    const [isDownloading, setIsDownloading] = useState(false)
    const [downloadPercentage, setDownloadPercentage] = useState(0)
    const [completedItems, setCompletedItems] = useState(0)

    const songTable = useRef<HTMLTableElement>(null);

    const [playlistData, setPlaylistData] = useState<IPlaylist | null>(null)
    const [playlistClips, setPlaylistClips] = useState<IPlaylistClip[]>([])

    const [footerView, setFooterView] = useState<1 | 2>(1)

    const getPlaylist = async () => {
        setIsGettingPLaylist(true)
        setPlaylistData(null)
        setPlaylistClips([])
        try {
            const data = await Suno.getSongsFromPlayList(playlistUrl)
            setPlaylistData(data[0])
            setPlaylistClips(data[1])
        } catch (err) {
            console.log(err)
            showError("Failed to fetch playlist data. Make sure you entered a valid link")
        }
        setIsGettingPLaylist(false)
    }

    const selectOutputFolder = async () => {
        const dir = await openDialog({
            title: "Select Output Folder",
            directory: true,
            canCreateDirectories: true
        })
        if (dir) setSaveFolder(dir)
    }

    const updateClipStatus = (id: string, status: IPlaylistClipStatus) => {
        setPlaylistClips((prevClips) =>
            prevClips.map((clip) =>
                clip.id === id ? { ...clip, status: status } : clip
            )
        )
    }

    const scrollToRow = (row: string) => {
        const node = songTable.current?.querySelector(`tr[data-id="row-${row}"]`)
        if (node) scrollIntoView(node, {
            scrollMode: "if-needed",
            behavior: "smooth",
            block: "end"
        })
    }

    const downloadPlaylist = async () => {
        setDownloadPercentage(0)
        setCompletedItems(0)
        setIsDownloading(true)

        //TODO: Proper error checking
        if (!playlistData || !playlistClips) return

        //Create the output directory if it doesn't exist
        const outputDir = await path.join(saveFolder, filenamify(playlistData.name))
        const tmpDir = await path.join(outputDir, "tmp")
        await ensureDir(outputDir)
        await ensureDir(tmpDir)

        //Reset the status of all clips
        setPlaylistClips((prevClips) =>
            prevClips.map((clip) => ({ ...clip, status: IPlaylistClipStatus.None }))
        )

        const limit = pLimit(5)
        const downloadPromises = playlistClips.map((song) => {
            return limit(async () => {
                updateClipStatus(song.id, IPlaylistClipStatus.Processing)

                scrollToRow(song.id)

                // ─── For Testing Only ────────────────────────
                //await delay(getRandomBetween(800, 2000))

                // ─── Live Downloading ────────────────────────
                const response = await fetch(song.audio_url)
                if (response.status !== 200) {
                    console.log("Failed to download song", song.audio_url)
                    updateClipStatus(song.id, IPlaylistClipStatus.Error)
                    return //continue
                }

                const songBuffer = await response.arrayBuffer()
                const songFileName = `${outputDir}\\${song.no.toString().padStart(2, "0")} - ${filenamify(song.title)}.mp3`
                writeFile(songFileName, songBuffer)
                //Try and download and inject the mp3 image
                const response2 = await fetch(song.image_url)
                if (response2.status === 200) {
                    const imageBuffer = await response2.arrayBuffer()
                    const imageFileName = `${tmpDir}\\${filenamify(song.id)}.jpg`
                    writeFile(imageFileName, imageBuffer)
                    addImageToMp3(songFileName, imageFileName)
                }

                // ─── Update The Playlist Data ────────────────
                updateClipStatus(song.id, IPlaylistClipStatus.Success)
                setCompletedItems((completedItems) => completedItems + 1)
                // const newPercentage = Math.ceil((song.no / playlistClips.length) * 100)
                // if (newPercentage > downloadPercentage) setDownloadPercentage(newPercentage)
            })
        })

        await Promise.all(downloadPromises)

        setIsDownloading(false)
        deletePath(tmpDir)

        //openCompleteModal()
        showSuccess("Playlist downloaded successfully")
    }

    const formatSecondsToTime = (seconds: number) => {
        const roundedSeconds = Math.round(seconds)
        const mins = Math.floor(roundedSeconds / 60)
        const secs = roundedSeconds % 60
        return `${mins}:${secs.toString().padStart(2, "0")}`
    }

    useEffect(() => {
        const initSavePath = async () => {
            const defaultSavePath = await path.audioDir()
            setSaveFolder(defaultSavePath)
        }
        initSavePath()
    }, [])

    useEffect(() => {
        //If we're downloading, show the download progress
        if (isDownloading) {
            setFooterView(2)
        } else {
            setFooterView(1)
        }
    }, [isDownloading])


    useEffect(() => {
        const totalItems = playlistClips.length
        const newPercentage = Math.ceil((completedItems / totalItems) * 100)
        setDownloadPercentage(newPercentage)
    }, [completedItems])


    // const updatePercentage = () => {
    //     const totalItems = playlistClips.length
    //     const completedItems = playlistClips.filter((clip) =>
    //         clip.status === IPlaylistClipStatus.Success
    //     ).length

    //     console.log(JSON.stringify(playlistClips.filter((clip) =>
    //         clip.status === IPlaylistClipStatus.Success
    //     ), null, 4))

    //     const percentage = Math.ceil((completedItems / totalItems) * 100)
    //     console.log(playlistClips, totalItems, completedItems, percentage)
    //     setDownloadPercentage(percentage)
    // }

    const openCompleteModal = () => modals.open({
        title: 'Operation complete',
        centered: true,
        withCloseButton: false,
        children: (
            <Stack gap={20}>
                <Text>Your playlist has been downloaded successfully</Text>
                <Flex justify="flex-end">
                    <Button onClick={() => modals.closeAll()}>Close</Button>
                </Flex>
            </Stack>
        )
    });

    return (
        <AppShell
            header={{ height: 50 }}
            padding="lg"
        >
            <AppShell.Header>
                <Box h="100%" data-tauri-drag-region>
                    <Flex justify="space-between" h="100%" w="100%" data-tauri-drag-region>
                        <Flex
                            h="100%"
                            w="100%"
                            justify="flex-start"
                            align="center"
                            style={{
                                userSelect: "none",
                            }}
                            data-tauri-drag-region>
                            <Group gap={6} ml={10}>
                                <IconVinyl />
                                <Text>Suno Music Downloader</Text>
                            </Group>
                        </Flex>
                        <CloseButton onClick={() => exit(1)} />
                    </Flex>
                </Box>
            </AppShell.Header>
            <AppShell.Main
                style={{
                    display: "flex",
                    flexDirection: "column", // Stacks children vertically
                    height: "100vh", // Full height of the viewport
                    overflow: "hidden", // Prevent overall layout overflow
                }}
            >
                {/* Top Section */}
                <SectionHeading number="1" title="Paste playlist link">
                    <Popover position="bottom-start" withArrow shadow="lg">
                        <Popover.Target>
                            <ActionIcon variant="subtle" size="sm" color="gray"><IconHelpCircle /></ActionIcon>
                        </Popover.Target>
                        <Popover.Dropdown>
                            <Group w={240} gap={4}>
                                <Image radius="md" src="./assets/copy-playlist.png" />
                                <Text>Navigate to your Suno playlist, and click the 'Copy playlist' button as shown</Text>
                            </Group>
                        </Popover.Dropdown>
                    </Popover>
                </SectionHeading>
                <Flex gap="sm" direction="row" mb={20}>
                    <TextInput
                        flex={1}
                        value={playlistUrl}
                        onChange={(event) => setPlaylistUrl(event.currentTarget.value)}
                        rightSection={<IconLink />}
                        disabled={isGettingPlaylist || isDownloading}
                    />
                    <Button
                        variant="filled"
                        loading={isGettingPlaylist}
                        onClick={getPlaylist}
                        disabled={isGettingPlaylist || isDownloading}
                    >
                        Get playlist songs
                    </Button>
                </Flex>

                {/* Central Section */}
                <SectionHeading number="2" title="Review songs" />
                <Flex
                    bg="dark.8"
                    mb={20}
                    style={{
                        flex: 1, // This grows to occupy remaining space
                        overflowY: "auto", // Scrollable if content exceeds
                        padding: "1rem", // Optional padding
                        borderRadius: "0.5rem",
                        flexFlow: "column"
                    }}
                >
                    <Table verticalSpacing="sm" ref={songTable}>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Img</Table.Th>
                                <Table.Th>Title</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>Length</Table.Th>
                                <Table.Th></Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {playlistData && playlistClips?.map((clip) => (
                                <Table.Tr key={clip.id} data-id={`row-${clip.id}`}>
                                    <Table.Td w={50}>
                                        <Image radius="sm" w={40} fit="contain" src={clip.image_url} />
                                    </Table.Td>
                                    <Table.Td>
                                        <Stack gap={0}>
                                            <Group gap={0}>
                                                <Text
                                                    fw={800} size="md"
                                                // variant="gradient"
                                                // gradient={{ from: "grape", to: "teal", deg: 45 }}
                                                >
                                                    {clip.title}
                                                </Text>
                                                <Badge size="xs"
                                                    variant="gradient"

                                                    gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
                                                    ml={6}
                                                >{clip.model_version}</Badge>
                                            </Group>
                                            <Text size="sm" c="dimmed" lineClamp={1}>{clip.tags}</Text>
                                        </Stack>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right" }}>
                                        <Text ff="monospace">
                                            {formatSecondsToTime(clip.duration)}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "center" }}>
                                        <StatusIcon status={clip.status} />
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                </Flex>

                {/* Bottom Section */}
                <SectionHeading number="3" title="Select folder and download">
                    <Popover position="bottom-start" withArrow shadow="lg">
                        <Popover.Target>
                            <ActionIcon variant="subtle" size="sm" color="gray"><IconHelpCircle /></ActionIcon>
                        </Popover.Target>
                        <Popover.Dropdown w={240}>
                            <Text>
                                In the selected directory, a new folder will be created with the playlist name. This folder will contain the downloaded songs.
                            </Text>
                        </Popover.Dropdown>
                    </Popover>
                </SectionHeading>
                <Flex gap="sm" direction="row" mb={20}>

                    <TextInput
                        flex={1}
                        value={saveFolder}
                        disabled={isDownloading}
                        readOnly
                        onClick={selectOutputFolder}
                        leftSection={<IconFolderFilled />}
                        style={{
                            pointer: "cursor",
                        }}
                    />
                    <Button
                        variant="filled"
                        disabled={isGettingPlaylist || isDownloading || (!playlistData)}
                        loading={isDownloading}
                        onClick={downloadPlaylist}
                    >
                        Download songs
                    </Button>
                </Flex>

                <Footer
                    firstComponent={
                        <Group gap={6}>
                            <Button leftSection={<IconBrandGithub />} variant="subtle" size="xs" component="a" href="http://www.github.com" target="_blank">Open source</Button>
                            <Divider orientation="vertical" />
                            <Button leftSection={<IconCoffee />} variant="subtle" size="xs" component="a" href="https://ko-fi.com/drummer_si" target="_blank">Buy me a coffee</Button>
                        </Group>
                    }
                    secondComponent={
                        <Stack
                            w="100%"
                            h={140}
                            gap={4}
                            pb={10}
                            mt={-5}
                        >
                            <Flex>
                                <Text size="xs">{downloadPercentage}%</Text>
                            </Flex>
                            <Progress value={downloadPercentage} animated />
                        </Stack>
                    }
                    currentView={footerView}
                />
            </AppShell.Main>
        </AppShell >
    )
}

// function App2() {
//     const [greetMsg, setGreetMsg] = useState("");
//     const [name, setName] = useState("");

//     async function greet() {
//         // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
//         setGreetMsg(await invoke("greet", { name }));
//     }

//     async function download() {

//         const response = await fetch("https://cdn1.suno.ai/2023b630-359f-4d44-9529-60c3b472c79a.mp3", {
//             method: "GET",
//         });
//         if (response.status !== 200) {
//             throw new Error("Failed to fetch the file.");
//         }

//         const fileData = new Uint8Array(await response.arrayBuffer())
//         await writeFile('test.mp3', fileData, { baseDir: BaseDirectory.Desktop })

//         console.log("SAVED")

//         sendNotification({
//             title: "Song downloaded",
//             body: "Song downloaded successfully",
//         })

//         // const file = await create('test.mp3', { baseDir: BaseDirectory.Desktop })
//         // await file.write(response.arrayBuffer)
//         // await file.close()
//         // console.log(response)


//         // const response = await fetch("https://cdn1.suno.ai/2023b630-359f-4d44-9529-60c3b472c79a.mp3", {
//         //     method: "GET",
//         //     //responseType: "ArrayBuffer", // Use ArrayBuffer for binary files
//         // });

//         // if (!response.data) {
//         //     throw new Error("Failed to fetch the file.");
//         // }

//         // const savePath = await dialog.save({
//         //     title: "Save File As",
//         //     defaultPath: "downloaded_file", // Default filename
//         // });

//         // if (!savePath) {
//         //     console.log("Save operation cancelled.");
//         //     return;
//         // }

//         // Step 3: Write the file to the selected location
//         // const fileData = new Uint8Array(response.data); // Convert ArrayBuffer to Uint8Array
//         // await fs.writeBinaryFile(savePath, fileData);

//         //console.log(`File successfully saved to: ${savePath}`);


//     }

//     return (
//         <main className="container">
//             <h1>Welcome to Tauri + React</h1>

//             <div className="row">
//                 <a href="https://vitejs.dev" target="_blank">
//                     <img src="/vite.svg" className="logo vite" alt="Vite logo" />
//                 </a>
//                 <a href="https://tauri.app" target="_blank">
//                     <img src="/tauri.svg" className="logo tauri" alt="Tauri logo" />
//                 </a>
//                 <a href="https://reactjs.org" target="_blank">
//                     <img src={reactLogo} className="logo react" alt="React logo" />
//                 </a>
//             </div>
//             <p>Click on the Tauri, Vite, and React logos to learn more.</p>

//             <form
//                 className="row"
//                 onSubmit={(e) => {
//                     e.preventDefault();
//                     greet();
//                 }}
//             >
//                 <input
//                     id="greet-input"
//                     onChange={(e) => setName(e.currentTarget.value)}
//                     placeholder="Enter a name..."
//                 />
//                 <button type="submit">Greet</button>

//                 <button onClick={download}>DOWNLOAD</button>
//             </form>
//             <p>{greetMsg}</p>
//         </main>
//     );
// }

export default App;

```

File Path: Sunodownloader/src/components/Footer.tsx
File Content:

```tsx
import { Box, Button, Divider, Flex, Group, Stack } from "@mantine/core"
import { FC, useEffect, useRef, useState } from "react"
import { IconBrandGithub, IconCoffee } from "@tabler/icons-react"

import { useScrollIntoView } from "@mantine/hooks"

interface Props {
    firstComponent: JSX.Element
    secondComponent: JSX.Element
    currentView: 1 | 2
}
const Footer: FC<Props> = (props) => {

    const { firstComponent, secondComponent, currentView } = props

    // Scroll hook
    const { targetRef: containerRef } = useScrollIntoView<HTMLDivElement>();


    // Handler to toggle scrolling
    // const toggleView = () => {
    //     const container = containerRef.current;
    //     if (!container) return;

    //     if (isFirstVisible) {
    //         container.scrollTo({
    //             top: container.offsetHeight, // Scroll to second div
    //             behavior: 'smooth',
    //         });
    //     } else {
    //         container.scrollTo({
    //             top: 0, // Scroll back to first div
    //             behavior: 'smooth',
    //         });
    //     }

    //     setIsFirstVisible((prev) => !prev);
    // };

    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const targetScrollTop = currentView === 1 ? 0 : container.offsetHeight
        //console.log("SCROLL TO", targetScrollTop)
        container.scrollTo({
            top: targetScrollTop,
            behavior: "smooth"
        })
    }, [currentView])


    return (
        <Box
            ref={containerRef}
            h={40}
            bg="dark.8"
            style={{
                overflow: "hidden", // Scrollable if content exceeds
                padding: "0.4rem", // Optional padding
                borderRadius: "0.5rem",
                flexFlow: "column"
            }}
        >
            <Stack>
                <Flex
                    //ref={firstDiv.targetRef}
                    justify="center"
                    wrap="nowrap"
                    align="center"
                >
                    {firstComponent}
                </Flex>
                <Flex
                    //ref={secondDiv.targetRef}
                    justify="center"
                    wrap="nowrap"
                    align="center"
                >
                    {secondComponent}
                </Flex>
            </Stack>
        </Box>
    )
}

export default Footer


```

File Path: Sunodownloader/src/components/SectionHeading.tsx
File Content:

```tsx
import { Badge, Group, Title } from "@mantine/core"

import { FC } from "react"

interface Props {
    number: string
    title: string
    children?: React.ReactNode
}
const SectionHeading: FC<Props> = (props) => {
    const { number, title, children } = props
    return (
        <Group pb={8} gap={8}>
            <Badge
                circle
                size="lg"
                variant="gradient"
                gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
            >{number}</Badge>
            <Title order={4}>{title}</Title>
            {children}
        </Group>
    )
}

export default SectionHeading
```

File Path: Sunodownloader/src/components/StatusIcon.tsx
File Content:

```tsx
import { IconCheck, IconSquareRoundedCheckFilled, IconSquareRoundedXFilled } from "@tabler/icons-react"
import { Loader, Text } from "@mantine/core"

import { FC } from "react"
import { IPlaylistClipStatus } from "../services/Suno"

interface Props {
    status: IPlaylistClipStatus
}

const StatusIcon: FC<Props> = (props) => {
    const { status } = props
    switch (status) {
        case IPlaylistClipStatus.None:
            return null

        case IPlaylistClipStatus.Processing:
            return <Loader size="xs" />

        case IPlaylistClipStatus.Success:
            return <Text c="green" mt={6}>
                <IconSquareRoundedCheckFilled />
            </Text>

        case IPlaylistClipStatus.Error:
            return <Text c="red" mt={6}>
                <IconSquareRoundedXFilled />
            </Text>

        default:
            return null
    }
}

export default StatusIcon
```

File Path: Sunodownloader/src/icons/icons8-playlist-96.png
File Content:

```png
�PNG


---

2nd one

File Path: Sunodl/check_artwork.py
File Content:
```py
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def check_embedded_artwork(mp3_file):
    """Checks if there is embedded artwork in the specified MP3 file."""
    try:
        audio = MP3(mp3_file, ID3=ID3)
        if audio.tags:
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    print(f"Artwork found in {mp3_file}: {tag.mime}, Description: {tag.desc}")
                    return True
        print(f"No artwork found in {mp3_file}.")
        return False
    except Exception as e:
        print(f"Error reading {mp3_file}: {e}")
        return False

def process_directory(downloads_dir):
    """Recursively processes the downloads directory to check for embedded artwork."""
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                check_embedded_artwork(mp3_file_path)

if __name__ == "__main__":
    downloads_dir = './downloads'  # Change this to your downloads directory if needed
    process_directory(downloads_dir)

```

File Path: Sunodl/embed_artwork.py
File Content:

```py
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def embed_artwork(mp3_file, image_file):
    """Embeds artwork into the specified MP3 file."""
    audio = MP3(mp3_file, ID3=ID3)

    # Read the image file
    with open(image_file, 'rb') as img:
        image_data = img.read()

    # Create an APIC tag for the artwork
    audio.tags.add(APIC(
        encoding=3,  # 3 is for ID3v2.3
        mime='image/jpeg',  # Change to 'image/png' if the image is a PNG
        type=3,  # 3 is for front cover
        desc='Cover',
        data=image_data
    ))

    # Save changes to the MP3 file
    audio.save()
    print(f"Artwork embedded in {mp3_file}")

def process_directory(downloads_dir):
    """Recursively processes the downloads directory for MP3 files and corresponding artwork."""
    for root, _, files in os.walk(downloads_dir):  # Recursively walk through the directory
        for file in files:
            if file.endswith('.mp3'):  # Check for MP3 files
                mp3_file_path = os.path.join(root, file)
                # Construct the expected JPG file path
                jpg_file_path = os.path.splitext(mp3_file_path)[0] + '.jpg'
                if os.path.exists(jpg_file_path):
                    embed_artwork(mp3_file_path, jpg_file_path)  # Embed artwork
                else:
                    print(f"No artwork found for {mp3_file_path}")

if __name__ == "__main__":
    downloads_dir = './downloads'  # Change this to your downloads directory if needed
    process_directory(downloads_dir)  # Start processing the directory

```

File Path: Sunodl/get_metadata.py
File Content:

```py
import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TXXX, APIC

def format_length(seconds):
    """Convert seconds to mm:ss format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def print_metadata(file_path):
    metadata = {}  # Initialize metadata dictionary
    try:
        audio = MP3(file_path, ID3=ID3)

        # Get the song ID
        song_id = audio.get('TXXX:Song ID', None)
        metadata['Song ID'] = song_id.text[0] if song_id else 'Not available'

        # Check for corresponding JPG file
        jpg_file_path = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(jpg_file_path):
            metadata['Album Art'] = jpg_file_path
        else:
            # Check for album art in the tags
            album_art = 'Not available'
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        album_art = 'Embedded art found'
                        break
            metadata['Album Art'] = album_art

        title = audio.tags.get('TIT2')
        artist = audio.tags.get('TPE1')
        upload_date = audio.tags.get('TXXX:Upload Date')  # Retrieve upload date
        length = audio.info.length
        bitrate = audio.info.bitrate

        print("Metadata for:", file_path)
        print("Song ID:", metadata['Song ID'])
        print("Title:", title.text[0] if title else "N/A")
        print("Artist:", artist.text[0] if artist else "N/A")
        print("Upload Date:", upload_date.text[0] if upload_date else "N/A")  # Display upload date
        print("Length:", format_length(length))
        print("Bitrate: {} kbps".format(bitrate // 1000))
        print("Artwork:", metadata['Album Art'])  # Print the final result for Album Art

    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")

def list_mp3_files(downloads_dir):
    """List all MP3 files in the downloads directory."""
    mp3_files = []
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

def process_directory(downloads_dir):
    """Process all MP3 files in the downloads directory."""
    mp3_files = list_mp3_files(downloads_dir)

    if not mp3_files:
        print("No MP3 files found in the downloads directory.")
    else:
        for file_path in mp3_files:
            print_metadata(file_path)

if __name__ == "__main__":
    downloads_dir = './downloads'
    # List MP3 files and process them
    process_directory(downloads_dir)

```

File Path: Sunodl/get_suno.py
File Content:

```py
# get_suno.py
import asyncio
from pyppeteer import launch
import argparse
import re
import os
import requests
import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TALB, TPE1, TXXX, APIC
from datetime import datetime
from tqdm import tqdm

def extract_song_id(url): # Moved to utils/url_utils.py
    """Extract the song ID from the URL."""
    match = re.search(r'song/([a-f0-9\-]+)', url)
    return match.group(1) if match else None

# def is_valid_url(url): # Moved to utils/url_utils.py
#     print("Checking valid URL in get_suno.py")
#     pattern = r'^https?://suno\.com/(song|playlist|@)[a-f0-9\-]+/?$'
#     is_valid = re.match(pattern, url) is not None
#     print(f"Validating URL: {url} | Is valid: {is_valid}")  # Debugging output
#     return is_valid

def is_valid_url(url):
    # Example check - you might want to adjust this based on your criteria
    return url.startswith("https://suno.com/")



async def fetch_song_data(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})

        # Get the full title
        full_title = await page.evaluate('document.title')
        # Split the title to get the song title and artist
        title, artist = full_title.split(' by @')
        artist = artist.split(' |')[0]  # Get the artist name before the separator

        audio_url = await page.evaluate('''
            () => {
                const metaTags = document.getElementsByTagName('meta');
                for (let tag of metaTags) {
                    if (tag.getAttribute('property') === 'og:audio') {
                        return tag.getAttribute('content');
                    }
                }
                return null;
            }
        ''')

        upload_date = await scrape_upload_date(page)
        album_art_url = await scrape_album_art(page)

        # Return the processed values
        return title.strip(), artist.strip(), upload_date, album_art_url
    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None, None, None, None
    finally:
        await browser.close()



async def scrape_upload_date(page): # Moved to suno/fetch.py
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')

    # Normalize the date format
    if upload_date_str:
        try:
            # Parse the date string
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            # Convert to ISO 8601 format
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None


async def scrape_album_art(page): # Moved to suno/fetch.py
    album_art_url = await page.evaluate('''
        () => {
            const metaTags = document.getElementsByTagName('meta');
            for (let tag of metaTags) {
                if (tag.getAttribute('property') === 'og:image') {
                    return tag.getAttribute('content');
                }
            }
            return null;
        }
    ''')
    return album_art_url

def extract_artist_and_title(title): # Moved to utils/metadata_utils.py
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None

def sanitize_filename(title): # Moved to utils/file_utils.py
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()

def ensure_directories_exist(artist): # Moved to utils/file_utils.py
    downloads_dir = './downloads'
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    artist_dir = os.path.join(downloads_dir, artist)
    if not os.path.exists(artist_dir):
        os.makedirs(artist_dir)

def download_album_art(album_art_url, artist, title): # Moved to utils/file_utils.py
    if not album_art_url:
        return None

    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    try:
        response = requests.get(album_art_url, stream=True)
        response.raise_for_status()

        # Save the album art in the artist's directory
        art_filename = sanitize_filename(title) + '.jpg'
        art_path = os.path.join('./downloads', artist, art_filename)

        # Use tqdm for progress bar
        total_size = int(response.headers.get('content-length', 0))
        with open(art_path, 'wb') as art_file, tqdm(
            desc=art_filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                art_file.write(data)
                bar.update(len(data))

        return art_path
    except Exception as e:
        print(f"Failed to download album art: {e}")
        return None

def download_song(mp3_url, artist, title, upload_date, album_art_path, song_id): # Moved to utils/file_utils.py
    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    sanitized_title = sanitize_filename(title)
    file_path = os.path.join('./downloads', artist, f'{sanitized_title}.mp3')

    if os.path.exists(file_path):
        return False, f'Skipped download. File already exists: {file_path}'

    try:
        response = requests.get(mp3_url, stream=True)
        response.raise_for_status()

        # Use tqdm for progress bar
        total_size = int(response.headers.get('content-length', 0))
        with open(file_path, 'wb') as file, tqdm(
            desc=sanitized_title,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

        # Set metadata using Mutagen
        audio = MP3(file_path, ID3=ID3)  # Use existing ID3 header if available
        audio.tags = ID3()  # Create ID3 tags if they don't exist
        audio.tags.add(TIT2(encoding=3, text=title))  # Title
        audio.tags.add(TPE1(encoding=3, text=artist))  # Artist
        audio.tags.add(TALB(encoding=3, text=''))  # Album
        audio.tags.add(TXXX(encoding=3, desc='Upload Date', text=upload_date))  # Upload Date
        audio.tags.add(TXXX(encoding=3, desc='Song ID', text=song_id))  # Song ID

        # Add album art if available
        if album_art_path:
            with open(album_art_path, 'rb') as img_file:
                img_data = img_file.read()
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img_data
                ))

        audio.save()  # Save the changes
        return True, f'Downloaded and tagged: {file_path}'
    except requests.exceptions.HTTPError as http_err:
        return False, f'HTTP error occurred: {http_err}'
    except Exception as err:
        return False, f'Other error occurred: {err}'


def log_song_data(title, artist, audio_url, upload_date, status, reason=""): # MOved to utils/metadata_utils.py
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "Failure" and reason:
        log_entry = f"{timestamp} | Title: {title} | Artist: {artist} | Audio URL: {audio_url} | Upload Date: {upload_date} | Status: {status} | Reason: {reason}\n"
    else:
        log_entry = f"{timestamp} | Title: {title} | Artist: {artist} | Audio URL: {audio_url} | Upload Date: {upload_date} | Status: {status}\n"

    with open("song_data.txt", "a") as f:
        f.write(log_entry)

def process_urls(urls): # Moved to suno/processing.py
    loop = asyncio.get_event_loop()
    for url in urls:
        title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(url))

        if title and audio_url:
            song_title, artist = extract_artist_and_title(title)
            song_id = extract_song_id(url)  # Extract the song ID
            print(f"Title: {song_title}")
            print(f"Artist: {artist}")
            print(f"Audio URL: {audio_url}")
            print(f"Upload Date: {upload_date}")

            # Download the album art
            album_art_path = download_album_art(album_art_url, artist, song_title)

            success, message = download_song(audio_url, artist, song_title, upload_date, album_art_path, song_id)
            print(message)
            if success:
                log_song_data(song_title, artist, audio_url, upload_date, "Success")
            else:
                reason = message.split('| Reason: ')[1] if '| Reason: ' in message else "Unknown reason"
                log_song_data(song_title, artist, audio_url, upload_date, "Failure", reason)
        else:
            print(f"Failed to extract song data for {url}.")


def main(url): # Added to main.py
    process_urls([url])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract song data from Suno page using Pyppeteer.')
    parser.add_argument('--url', type=str, help='URL of the Suno song, playlist, or artist page')
    parser.add_argument('--playlist', action='store_true', help='Prompt for multiple Suno song URLs')
    args = parser.parse_args()

    if args.url:
        main(args.url)
    elif args.playlist:
        urls = []
        while True:
            url = input("Please enter the Suno song, playlist, or artist URL (or just hit Enter to stop): ")
            if url == '':
                break
            if is_valid_url(url):
                urls.append(url)
            else:
                print("Invalid URL. Please enter a valid Suno song, playlist, or artist URL.")

        urls = list(set(urls))  # Remove duplicates before processing
        process_urls(urls)
    else:
        url = input("Please enter the Suno song, playlist, or artist URL: ")
        main(url)

```

File Path: Sunodl/main.py
File Content:

```py
from suno.processing import process_urls
from utils.artwork_utils import process_directory as process_artwork_directory
from utils.get_metadata_utils import process_directory as process_metadata_directory
from utils.url_utils import is_valid_url




def _menu_clear_log():
    """Clear the song_data.txt log file."""
    try:
        with open("song_data.txt", "w") as log_file:
            log_file.write("")
        print("Log file cleared successfully.")
    except Exception as e:
        print(f"Error clearing log file: {e}")

def _menu_download_song():
    """Download a single song from a URL."""
    url = input("Enter the song URL: ")
    if is_valid_url(url):
        process_urls([url])
    else:
        print("Invalid URL.")

def _menu_download_playlist():
    """Download a playlist from a URL."""
    url = input("Enter the playlist URL: ")
    if is_valid_url(url):
        process_urls([url])
    else:
        print("Invalid URL.")

def _menu_download_artist_collection():
    """Download an artist collection from a URL."""
    url = input("Enter the artist collection URL: ")
    if is_valid_url(url):
        process_urls([url])
    else:
        print("Invalid URL.")

def main():
    downloads_dir = './downloads'  # Define the downloads directory here

    while True:
        print("\nChoose an option:")
        print("1. Check for embedded artwork in MP3 files")
        print("2. Embed artwork in MP3 files")
        print("3. Get metadata for MP3 files")
        print("4. View Log (song_data.txt)")
        print("5. Download Song")
        print("6. Download Playlist")
        print("7. Download Artist Collection")
        print("8. Clear Log")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            process_artwork_directory(downloads_dir)  # Check for embedded artwork
        elif choice == '2':
            process_artwork_directory(downloads_dir)  # Embed artwork
        elif choice == '3':
            process_metadata_directory(downloads_dir)  # Process metadata
        elif choice == '4':
            try:
                with open("song_data.txt", "r") as log_file:
                    print(log_file.read())
            except FileNotFoundError:
                print("Log file not found.")
        elif choice == '5':
            _menu_download_song()
        elif choice == '6':
            _menu_download_playlist()
        elif choice == '7':
            _menu_download_artist_collection()
        elif choice == '8':
            _menu_clear_log()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

```

File Path: Sunodl/README.md
File Content:

```md
# download_suno

## Description

This project automates the processing of [Suno AI](https://suno.com/) MP3 files, including downloading songs, checking for and embedding album artwork, and retrieving metadata. Users can interact with the system via a menu interface to perform operations such as embedding artwork, viewing metadata, and downloading tracks or collections from provided URLs.

### Key Features

- **Download Management**: Download individual songs, playlists, or artist collections from URLs.
- **Artwork Handling**: Check for embedded album artwork in MP3 files and embed artwork from local JPG files.
- **Metadata Extraction**: Extract and display metadata from MP3 files, including song title, artist, and album art presence.
- **Log Management**: View and clear logs of processed songs.

### Technologies Used

- **Python** for scripting and logic control.
- **Mutagen** library for MP3 metadata and artwork handling.
- **OS Library** for directory navigation and file manipulation.

### Installation Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/skyler-saville/download_suno
   cd <repository-directory>
   ```

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Ensure you have the necessary directory structure with a `downloads` folder where MP3 files will be processed.

## Usage Instructions

1. Run the main script to interact with the project:

   ```bash
   make run
   ```

2. Use the following options from the menu:
   - `1` to check for embedded artwork in MP3 files.
   - `2` to embed artwork from corresponding JPG files.
   - `3` to extract and display metadata from MP3 files.
   - `5-7` for downloading a song, playlist, or artist collection via URL input.
   - `4` to view the log of processed songs.
   - `8` to clear the log.
   - `0` to exit the application.

## Code Overview

1. **Main Script (`main.py`)**: Handles user interaction through a menu and allows the user to download songs, check metadata, and embed artwork.
2. **Metadata Processing (`get_metadata.py`)**: Extracts metadata such as song ID, title, artist, and album art presence from MP3 files. It also formats song length in mm:ss format.
3. **Artwork Check (`check_artwork.py`)**: Recursively checks for embedded artwork in MP3 files.
4. **Embed Artwork (`embed_artwork.py`)**: Embeds artwork into MP3 files from corresponding local image files (JPG format).

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Add some feature"
   ```

4. Push to the branch:

   ```bash
   git push origin feature/your-feature
   ```

5. Open a pull request for review.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file in the root directory for more details.

---

```
File Path: Sunodl/suno/.gitignore
File Content:
```

config.py
cli.py
core.py
helpers.py

```
File Path: Sunodl/suno/cli.py
File Content:
```py

```

File Path: Sunodl/suno/config.py
File Content:

```py

```

File Path: Sunodl/suno/core.py
File Content:

```py

```

File Path: Sunodl/suno/exceptions.py
File Content:

```py
class DownloadError(Exception):
    pass

class MetadataError(Exception):
    pass

```

File Path: Sunodl/suno/fetch.py
File Content:

```py
# suno/fetch.py
from datetime import datetime
from pyppeteer import launch
from utils.url_utils import extract_song_id, is_valid_url

async def fetch_song_data(url): # This moved to suno/fetch.py
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})

        title = await page.evaluate('document.title')
        audio_url = await page.evaluate('''
            () => {
                const metaTags = document.getElementsByTagName('meta');
                for (let tag of metaTags) {
                    if (tag.getAttribute('property') === 'og:audio') {
                        return tag.getAttribute('content');
                    }
                }
                return null;
            }
        ''')

        upload_date = await scrape_upload_date(page)
        album_art_url = await scrape_album_art(page)

        return title, audio_url, upload_date, album_art_url
    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None, None, None, None
    finally:
        await browser.close()


async def scrape_upload_date(page):  # This moved to suno/fetch.py
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')

    # Normalize the date format
    if upload_date_str:
        try:
            # Parse the date string
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            # Convert to ISO 8601 format
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None


async def scrape_album_art(page):  # This moved to suno/fetch.py
    album_art_url = await page.evaluate('''
        () => {
            const metaTags = document.getElementsByTagName('meta');
            for (let tag of metaTags) {
                if (tag.getAttribute('property') === 'og:image') {
                    return tag.getAttribute('content');
                }
            }
            return null;
        }
    ''')
    return album_art_url



```

File Path: Sunodl/suno/helpers.py
File Content:

```py

```

File Path: Sunodl/suno/processing.py
File Content:

```py
# suno/processing.py
import asyncio

from utils.artist_song_utils import fetch_artist_songs
from utils.fetch_utils import extract_artist_and_title, fetch_song_data
from utils.file_utils import download_song
from utils.logging_utils import log_song_data
from utils.playlist_utils import fetch_playlist_songs


def process_urls(urls):
    loop = asyncio.get_event_loop()
    success_count = 0
    failure_count = 0

    for url in urls:
        if 'playlist' in url:
            song_urls = loop.run_until_complete(fetch_playlist_songs(url))
            for song_url in song_urls:
                title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(song_url))

                if title and audio_url:
                    song_title, artist = extract_artist_and_title(title)
                    print(f"Title: {song_title}")
                    print(f"Artist: {artist}")
                    print(f"Audio URL: {audio_url}")
                    print(f"Upload Date: {upload_date}")
                    print(f"Album Art URL: {album_art_url}")

                    # Download the song and log the result
                    success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                    print(message)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1

                    # Log the song data
                    log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)
                else:
                    print(f"Failed to extract song data for {song_url}.")
                    log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract playlist")
        elif '@' in url:
            song_urls = loop.run_until_complete(fetch_artist_songs(url))
            for song_url in song_urls:
                title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(song_url))

                if title and audio_url:
                    song_title, artist = extract_artist_and_title(title)
                    print(f"Title: {song_title}")
                    print(f"Artist: {artist}")
                    print(f"Audio URL: {audio_url}")
                    print(f"Upload Date: {upload_date}")
                    print(f"Album Art URL: {album_art_url}")

                    # Download the song and log the result
                    success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                    print(message)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1

                    # Log the song data
                    log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)
                else:
                    print(f"Failed to extract song data for {song_url}.")
                    log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract artist page")
        else:
            title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(url))

            if title and audio_url:
                song_title, artist = extract_artist_and_title(title)
                print(f"Title: {song_title}")
                print(f"Artist: {artist}")
                print(f"Audio URL: {audio_url}")
                print(f"Upload Date: {upload_date}")
                print(f"Album Art URL: {album_art_url}")

                # Download the song and log the result
                success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                print(message)
                if success:
                    success_count += 1
                else:
                    failure_count += 1

                # Log the song data
                log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)


            else:
                print(f"Failed to extract song data for {url}.")
                log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract song data")

    print(f"\nSummary: {success_count} songs downloaded successfully, {failure_count} failed.")

def main(url):
    process_urls([url])

```

File Path: Sunodl/suno/**init**.py
File Content:

```py

```

File Path: Sunodl/tests/test_check_artwork.py
File Content:

```py

```

File Path: Sunodl/tests/test_embed_artwork.py
File Content:

```py

```

File Path: Sunodl/tests/test_get_suno.py
File Content:

```py
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from Sunodl.get_suno import fetch_song_data, scrape_upload_date, scrape_album_art, extract_artist_and_title, is_valid_url

SONG_URL = "https://suno.com/song/6a6bdd56-d583-4e0a-9869-b98a8c72a37b"
PLAYLIST_URL = "https://suno.com/playlist/99e5d0c6-b1f7-451d-830d-5c272d114cd6"
ARTIST_URL = "https://suno.com/@happygoth"

@pytest.mark.asyncio
async def test_fetch_song_data():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        mock_page.evaluate.side_effect = [
            "Shadows of the Holler by @timmo",  # Title without the '| Suno'
            "https://cdn1.suno.ai/6a6bdd56-d583-4e0a-9869-b98a8c72a37b.mp3",  # Correct Audio URL
            "February 26, 2024 at 09:51 AM",  # Correct Upload Date
            "https://cdn2.suno.ai/image_large_768adf51-ba69-44c7-9c6a-a488babb73e7.jpeg"  # Optional Album Art URL
        ]

        result = await fetch_song_data(SONG_URL)

        assert result == (
            "Shadows of the Holler",
            "timmo",
            "2024-02-26T09:51:00",
            "https://cdn2.suno.ai/image_large_768adf51-ba69-44c7-9c6a-a488babb73e7.jpeg"
        )


@pytest.mark.asyncio
async def test_scrape_upload_date():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        future = asyncio.Future()
        future.set_result("January 1, 2023 at 12:00 PM")
        mock_page.evaluate.return_value = future

        upload_date = await scrape_upload_date(mock_page)
        assert upload_date == "2023-01-01T12:00:00"

@pytest.mark.asyncio
async def test_scrape_album_art():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        future = asyncio.Future()
        future.set_result("http://album.art/url.jpg")
        mock_page.evaluate.return_value = future

        album_art_url = await scrape_album_art(mock_page)
        assert album_art_url == "http://album.art/url.jpg"

def test_extract_artist_and_title():
    title = "Test Song Title by @TestArtist - Some Info"
    song_title, artist = extract_artist_and_title(title)
    assert song_title == "Test_Song_Title"
    assert artist == "TestArtist"

def test_is_valid_url():
    assert is_valid_url(SONG_URL) == True
    assert is_valid_url(PLAYLIST_URL) == True
    assert is_valid_url(ARTIST_URL) == True
    assert is_valid_url("https://invalid-url.com") == False

```

File Path: Sunodl/tests/test_utils/test_artwork_utils.py
File Content:

```py
# tests/test_utils/test_artwork_utils.py

import os
import pytest
from utils.artwork_utils import embed_artwork, check_embedded_artwork, process_directory
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

@pytest.fixture
def setup_mp3_with_artwork(tmp_path):
    """Fixture to create a temporary valid MP3 file with a temporary image file."""
    # Path for the temporary files
    mp3_file = tmp_path / "test_song.mp3"
    image_file = tmp_path / "cover.jpg"

    # Create a valid MP3 file (using a small sample MP3 for testing)
    with open(mp3_file, 'wb') as f:
        f.write(b'\x49\x44\x33\x03\x00\x00\x00\x00\x00\x00\x00\x00')  # Minimal ID3 header

    # Create a dummy image file
    with open(image_file, 'wb') as f:
        f.write(b'\0' * 1024)  # Just create a dummy image file

    return mp3_file, image_file

def test_embed_artwork(setup_mp3_with_artwork):
    mp3_file, image_file = setup_mp3_with_artwork
    embed_artwork(mp3_file, image_file)

    # Check if artwork was embedded
    audio = MP3(mp3_file, ID3=ID3)
    assert any(isinstance(tag, APIC) for tag in audio.tags.values())

def test_check_embedded_artwork(setup_mp3_with_artwork):
    mp3_file, image_file = setup_mp3_with_artwork
    embed_artwork(mp3_file, image_file)

    assert check_embedded_artwork(mp3_file) is True

def test_process_directory(tmp_path):
    """Test that process_directory correctly processes MP3 files and embeds artwork."""
    mp3_file = tmp_path / "test_song.mp3"
    image_file = tmp_path / "cover.jpg"

    # Create a valid MP3 file
    with open(mp3_file, 'wb') as f:
        f.write(b'\x49\x44\x33\x03\x00\x00\x00\x00\x00\x00\x00\x00')  # Minimal ID3 header

    # Create a dummy image file
    with open(image_file, 'wb') as f:
        f.write(b'\0' * 1024)

    # Call process_directory
    os.makedirs(tmp_path / "downloads", exist_ok=True)
    mp3_dest = (tmp_path / "downloads" / "test_song.mp3")
    mp3_file.rename(mp3_dest)

    jpg_dest = (tmp_path / "downloads" / "cover.jpg")
    image_file.rename(jpg_dest)

    # Run the function
    process_directory(tmp_path / "downloads")

    # Verify that artwork was embedded
    assert check_embedded_artwork(mp3_dest) is True

```

File Path: Sunodl/tests/test_utils/test_fetch_utils.py
File Content:

```py

```

File Path: Sunodl/tests/test_utils/test_file_utils.py
File Content:

```py

```

File Path: Sunodl/tests/test_utils/test_metadata_utils.py
File Content:

```py

```

File Path: Sunodl/tests/test_utils/test_url_utils.py
File Content:

```py

```

File Path: Sunodl/tests/test_utils/**init**.py
File Content:

```py

```

File Path: Sunodl/tests/**init**.py
File Content:

```py

```

File Path: Sunodl/utils/artist_song_utils.py
File Content:

```py
from pyppeteer import launch


async def fetch_artist_songs(artist_url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()

        await page.goto(artist_url, {'waitUntil': 'networkidle2'})

        # Extract all song URLs from the artist's page
        song_links = await page.evaluate('''
            () => {
                const links = [];
                const songElements = document.querySelectorAll('a[href^="/song/"]');
                songElements.forEach(el => links.push('https://suno.com' + el.getAttribute('href')));
                return links;
            }
        ''')
        return song_links
    except Exception as e:
        print(f"Error fetching artist data for {artist_url}: {e}")
        return []
    finally:
        await browser.close()
```

File Path: Sunodl/utils/artwork_utils.py
File Content:

```py
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def embed_artwork(mp3_file, image_file):
    """Embeds artwork into the specified MP3 file."""
    audio = MP3(mp3_file, ID3=ID3)

    # Read the image file
    with open(image_file, 'rb') as img:
        image_data = img.read()

    # Create an APIC tag for the artwork
    audio.tags.add(APIC(
        encoding=3,  # 3 is for ID3v2.3
        mime='image/jpeg',  # Change to 'image/png' if the image is a PNG
        type=3,  # 3 is for front cover
        desc='Cover',
        data=image_data
    ))

    # Save changes to the MP3 file
    audio.save()
    print(f"Artwork embedded in {mp3_file}")

def check_embedded_artwork(mp3_file):
    """Checks if there is embedded artwork in the specified MP3 file."""
    try:
        audio = MP3(mp3_file, ID3=ID3)
        if audio.tags:
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    print(f"Artwork found in {mp3_file}: {tag.mime}, Description: {tag.desc}")
                    return True
        print(f"No artwork found in {mp3_file}.")
        return False
    except Exception as e:
        print(f"Error reading {mp3_file}: {e}")
        return False

def process_directory(downloads_dir):
    """Recursively processes the downloads directory for MP3 files."""
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                # Check for embedded artwork
                check_embedded_artwork(mp3_file_path)
                # Construct the expected JPG file path for embedding
                jpg_file_path = os.path.splitext(mp3_file_path)[0] + '.jpg'
                if os.path.exists(jpg_file_path):
                    embed_artwork(mp3_file_path, jpg_file_path)  # Embed artwork
                else:
                    print(f"No artwork found for {mp3_file_path}")

if __name__ == "__main__":
    downloads_dir = './downloads'  # Change this to your downloads directory if needed
    process_directory(downloads_dir)  # Start processing the directory

```

File Path: Sunodl/utils/fetch_utils.py
File Content:

```py
import os

import re
from utils.file_utils import download_album_art, download_file, sanitize_filename
from utils.get_metadata_utils import embed_metadata
from utils.logging_utils import log_song_data
from pyppeteer import launch
from datetime import datetime


async def fetch_song_data(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})

        title = await page.evaluate('document.title')
        audio_url = await page.evaluate('''
            () => {
                const metaTags = document.getElementsByTagName('meta');
                for (let tag of metaTags) {
                    if (tag.getAttribute('property') === 'og:audio') {
                        return tag.getAttribute('content');
                    }
                }
                return null;
            }
        ''')

        upload_date = await scrape_upload_date(page)
        album_art_url = await scrape_album_art(page)

        return title, audio_url, upload_date, album_art_url
    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None, None, None, None
    finally:
        await browser.close()


async def scrape_upload_date(page):
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')

    # Normalize the date format
    if upload_date_str:
        try:
            # Parse the date string
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            # Convert to ISO 8601 format
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None



async def scrape_album_art(page):
    album_art_url = await page.evaluate('''
        () => {
            const metaTags = document.getElementsByTagName('meta');
            for (let tag of metaTags) {
                if (tag.getAttribute('property') === 'og:image') {
                    return tag.getAttribute('content');
                }
            }
            return null;
        }
    ''')
    return album_art_url

async def scrape_upload_date(page):
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')

    if upload_date_str:
        try:
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None


def extract_artist_and_title(title):
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None


async def process_song(url):
    title, audio_url, upload_date, album_art_url = await fetch_song_data(url)

    if title and audio_url:
        song_title, artist = extract_artist_and_title(title)

        print(f"Processing song: {song_title} by {artist}")
        print(f"Audio URL: {audio_url}")
        print(f"Upload Date: {upload_date}")

        # Download the album art
        album_art_path = await download_album_art(album_art_url, artist, song_title)

        # Download the song
        sanitized_title = sanitize_filename(song_title)
        file_path = f'./downloads/{artist}/{sanitized_title}.mp3'

        if os.path.exists(file_path):
            print(f"Skipped download. File already exists: {file_path}")
            log_song_data(song_title, artist, audio_url, upload_date, "Failure", "File already exists")
            return

        try:
            await download_file(audio_url, file_path)
            print(f"Downloaded song to: {file_path}")

            # Embed metadata
            embed_metadata(file_path, song_title, artist, upload_date, album_art_path)
            log_song_data(song_title, artist, audio_url, upload_date, "Success")

        except Exception as e:
            print(f"Error downloading song: {e}")
            log_song_data(song_title, artist, audio_url, upload_date, "Failure", str(e))
    else:
        print(f"Failed to extract song data for {url}.")
        log_song_data("", "", "", "", "Failure", "Failed to extract song data")

```

File Path: Sunodl/utils/file_utils.py
File Content:

```py
import os
import re
import mutagen
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TXXX, APIC
from tqdm import tqdm

def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()


def ensure_directories_exist(artist):
    # Use an absolute path for downloads
    downloads_dir = os.path.join(os.getcwd(), 'downloads')

    # Create downloads directory if it doesn't exist
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        print(f'Created directory: {downloads_dir}')

    # Create artist directory within downloads
    artist_dir = os.path.join(downloads_dir, artist)
    if not os.path.exists(artist_dir):
        os.makedirs(artist_dir)
        print(f'Created directory: {artist_dir}')


def download_album_art(album_art_url, artist, title): # unused. The download song function now handles the artwork as well
    if not album_art_url:
        return None

    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    try:
        response = requests.get(album_art_url)
        response.raise_for_status()

        # Save the album art in the artist's directory
        art_filename = sanitize_filename(title) + '.jpg'
        art_path = os.path.join('./downloads', artist, art_filename)

        with open(art_path, 'wb') as art_file:
            art_file.write(response.content)

        return art_path
    except Exception as e:
        print(f"Failed to download album art: {e}")
        return None

def download_song(mp3_url, artist, title, upload_date, album_art_url):
    ensure_directories_exist(artist)

    sanitized_title = sanitize_filename(title)
    sanitized_artist = sanitize_filename(artist)
    mp3_file_path = os.path.join('./downloads', sanitized_artist, f'{sanitized_title}.mp3')
    album_art_file_path = os.path.join('./downloads', sanitized_artist, f'{sanitized_title}.jpeg')

    if os.path.exists(mp3_file_path) and os.path.exists(album_art_file_path):
        return False, f'Skipped download. Files already exist: {mp3_file_path}, {album_art_file_path}'

    try:
        # Download the MP3 file
        download_file(mp3_url, mp3_file_path)

        # Download the album art
        if album_art_url:
            download_file(album_art_url, album_art_file_path)

        # Set metadata using Mutagen
        audio = MP3(mp3_file_path, ID3=ID3)
        audio.tags = ID3()  # Create ID3 tags if they don't exist
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=''))
        audio.tags.add(TXXX(encoding=3, desc='Upload Date', text=upload_date))

        # Embed the album art
        if os.path.exists(album_art_file_path):
            with open(album_art_file_path, 'rb') as img_file:
                img_data = img_file.read()
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img_data
                ))

        audio.save()
        return True, f'Downloaded and tagged: {mp3_file_path}'
    except requests.exceptions.HTTPError as http_err:
        return False, f'HTTP error occurred: {http_err}'
    except IOError as io_err:
        return False, f'File I/O error occurred: {io_err}'
    except mutagen.MutagenError as mutagen_err:
        return False, f'Mutagen error occurred: {mutagen_err}'
    except Exception as err:
        return False, f'Other error occurred: {err}'


def check_embedded_artwork(mp3_file):
    """Checks if there is embedded artwork in the specified MP3 file."""
    try:
        audio = MP3(mp3_file, ID3=ID3)
        if audio.tags:
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    print(f"Artwork found in {mp3_file}: {tag.mime}, Description: {tag.desc}")
                    return True
        print(f"No artwork found in {mp3_file}.")
        return False
    except Exception as e:
        print(f"Error reading {mp3_file}: {e}")
        return False

def process_directory(downloads_dir):
    """Recursively processes the downloads directory to check for embedded artwork."""
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                check_embedded_artwork(mp3_file_path)

def download_file(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
```

File Path: Sunodl/utils/get_metadata_utils.py
File Content:

```py
# utils/get_metadata_utils.py

import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TXXX, APIC

def format_length(seconds):
    """Convert seconds to mm:ss format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def print_metadata(file_path):
    metadata = {}  # Initialize metadata dictionary
    try:
        audio = MP3(file_path, ID3=ID3)

        # Get the song ID
        song_id = audio.get('TXXX:Song ID', None)
        metadata['Song ID'] = song_id.text[0] if song_id else 'Not available'

        # Check for corresponding JPG file
        jpg_file_path = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(jpg_file_path):
            metadata['Album Art'] = jpg_file_path
        else:
            # Check for album art in the tags
            album_art = 'Not available'
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        album_art = 'Embedded art found'
                        break
            metadata['Album Art'] = album_art

        title = audio.tags.get('TIT2')
        artist = audio.tags.get('TPE1')
        upload_date = audio.tags.get('TXXX:Upload Date')  # Retrieve upload date
        length = audio.info.length
        bitrate = audio.info.bitrate

        print("Metadata for:", file_path)
        print("Song ID:", metadata['Song ID'])
        print("Title:", title.text[0] if title else "N/A")
        print("Artist:", artist.text[0] if artist else "N/A")
        print("Upload Date:", upload_date.text[0] if upload_date else "N/A")  # Display upload date
        print("Length:", format_length(length))
        print("Bitrate: {} kbps".format(bitrate // 1000))
        print("Artwork:", metadata['Album Art'])  # Print the final result for Album Art

    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")

def list_mp3_files(downloads_dir):
    """List all MP3 files in the downloads directory."""
    mp3_files = []
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

def process_directory(downloads_dir):
    """Process all MP3 files in the downloads directory."""
    mp3_files = list_mp3_files(downloads_dir)

    if not mp3_files:
        print("No MP3 files found in the downloads directory.")
    else:
        for file_path in mp3_files:
            print_metadata(file_path)


def embed_metadata(file_path, title, artist, upload_date, album_art_path):
    audio = MP3(file_path, ID3=ID3)
    audio.tags = ID3()  # Create ID3 tags if they don't exist
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TALB(encoding=3, text=''))
    audio.tags.add(TXXX(encoding=3, desc='Upload Date', text=upload_date))

    if album_art_path:
        with open(album_art_path, 'rb') as img_file:
            img_data = img_file.read()
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img_data
            ))

    audio.save()  # Save the changes
```

File Path: Sunodl/utils/logging_utils.py
File Content:

```py
from datetime import datetime


def log_song_data(title, artist, audio_url, upload_date, status, reason=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"{timestamp} | Title: {title} | Artist: {artist} | "
        f"Audio URL: {audio_url} | Upload Date: {upload_date} | "
        f"Status: {status}"
    )
    if status == "Failure" and reason:
        log_entry += f" | Reason: {reason}"

    log_entry += "\n"

    try:
        with open("song_data.txt", "a") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Failed to write to log: {e}")
```

File Path: Sunodl/utils/metadata_utils.py
File Content:

```py
import os
import re
from datetime import datetime

def extract_artist_and_title(title):
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None


```

File Path: Sunodl/utils/playlist_utils.py
File Content:

```py
from pyppeteer import launch

from utils.fetch_utils import fetch_song_data
from utils.logging_utils import log_song_data
from utils.metadata_utils import extract_artist_and_title


async def fetch_playlist_songs(playlist_url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()

        await page.goto(playlist_url, {'waitUntil': 'networkidle2'})

        # Extract all song URLs from the playlist
        song_links = await page.evaluate('''
            () => {
                const links = [];
                const songElements = document.querySelectorAll('a[href^="/song/"]');
                songElements.forEach(el => links.push('https://suno.com' + el.getAttribute('href')));
                return links;
            }
        ''')
        return song_links
    except Exception as e:
        print(f"Error fetching playlist data for {playlist_url}: {e}")
        return []
    finally:
        await browser.close()

```

File Path: Sunodl/utils/url_utils.py
File Content:

```py
import re

def is_valid_url(url):
    pattern = r'^https?://suno\.com/song/[a-f0-9\-]+$'
    playlist_pattern = r'^https?://suno\.com/playlist/[a-f0-9\-]+$'
    artist_pattern = r'^https?://suno\.com/@[a-zA-Z0-9_-]+$'
    return (re.match(pattern, url) or
            re.match(playlist_pattern, url) or
            re.match(artist_pattern, url))


def extract_song_id(url):
    """Extract the song ID from the URL."""
    match = re.search(r'song/([a-f0-9\-]+)', url)
    return match.group(1) if match else None

```

File Path: Suno Tools/download_cover_art.js
File Content:

```js
import * as fs from 'fs/promises';
import { parse } from 'node-html-parser';
import path from 'path';

const BASE_PATH = 'C:\\Users\\User\\Documents\\Github\\suno_ai_downloader\\cover_art';

async function main() {
  const filePath = 'C://Users//User//Documents//Github//suno_ai_downloader//unique_songs.txt'; // Path to your URL list

  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const urls = fileContent.split(/\s+/).filter(line => line.trim() !== '');

    for (const url of urls) {
      const uuid = url.match(
        /\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b/,
      );

      if (!uuid) {
        console.error('Invalid UUID:', url);
        continue;
      }

      console.log('Processing UUID:', uuid[0]);
      const formattedUrl = `https://suno.com/song/${uuid[0]}`;

      try {
        await fetchAndSaveCoverArt(formattedUrl); //  Call the function to fetch and save
      } catch (err) {
        console.error(`Error processing ${formattedUrl}:`, err);
      }
    }
  } catch (err) {
    console.error('Error reading file:', err);
  }
}

async function fetchAndSaveCoverArt(url) {
  const result = await fetch(url);
  if (!result.ok) {
    console.error('Failed to fetch:', url);
    return;
  }
  const html = await result.text();
  const root = parse(html);

  let pushedData = '';

  // Loop over all script tags, same logic as your original script
  for (const script of root.querySelectorAll('script')) {
    if (!script.text.startsWith('self.__next_f.push([')) {
      continue;
    }

    const data = script.text.match(
      /\s*self\.__next_f.push\(\[\s*1,\s*"(?<wanted>.*)",?\s*\]\);?/m,
    );
    if (data && data[1]) {
      const better = JSON.parse(`"${data[1]}"`);
      pushedData += better;
    }
  }

  const start = pushedData.indexOf('{"clip":');
  if (start === -1) {
    console.error('Failed to find clip data in', url);
    return;
  }

  const clip = pushedData.slice(start);
  let json = null;
  let endCut = 0;

  try {
    json = JSON.parse(clip);
  } catch (e) {
    const position = e.message.match(/position (\d+)/);
    if (position) {
      endCut = parseInt(position[1]);
    } else {
      console.error('Failed to parse json:', e);
      return;
    }

    try {
      json = JSON.parse(clip.slice(0, endCut));
    } catch (e) {
      console.error('Failed to parse json again:', e);
      return;
    }
  }
    if(!json || !json.clip) {
        console.error('Failed to parse clip data:', url);
        return;
    }

  await doImage(json.clip); // Call doImage with the clip data
}


async function doImage(data) {
  const artBuffer = await fetch(data.image_large_url).then((res) =>
    res.arrayBuffer(),
  );

  // Get the song title
  const songTitle = data.title;

  // Create the song directory
  const songDirPath = path.join(BASE_PATH, songTitle);
  await fs.mkdir(songDirPath, { recursive: true });

  // Define the base filename (only the song title)
  let baseFilename = songTitle;
  let filename = path.join(songDirPath, `${baseFilename}.jpg`);

  // Check if file exists, and use Roman numerals for duplicates
  filename = await getUniqueFilenameRoman(filename, songDirPath, baseFilename);

  // Save the image file
  await fs.writeFile(filename, Buffer.from(artBuffer));
  console.log('Wrote cover art:', filename);
}

// Function to get a unique filename using Roman numerals
async function getUniqueFilenameRoman(filepath, dir, baseFilename) {
    let ext = path.extname(filepath);
    let filename = path.basename(filepath, ext);
    let counter = 0; // Start at 0, first instance will be without Roman Numeral
    let newFilename = path.join(dir, `${baseFilename}${ext}`);

    while (await fileExists(newFilename)) {
        counter++;
        const roman = toRoman(counter);
        newFilename = path.join(dir, `${baseFilename} ${roman}${ext}`);
    }

    return newFilename;
}

// Helper function to convert numbers to Roman numerals
function toRoman(num) {
  const romanMap = {
    1: 'I',
    4: 'IV',
    5: 'V',
    9: 'IX',
    10: 'X',
    40: 'XL',
    50: 'L',
    90: 'XC',
    100: 'C',
    400: 'CD',
    500: 'D',
    900: 'CM',
    1000: 'M',
  };

  let result = '';
  const decimalValues = Object.keys(romanMap).map(Number).sort((a, b) => b - a);

  for (const decimal of decimalValues) {
    while (num >= decimal) {
      result += romanMap[decimal];
      num -= decimal;
    }
  }

  return result;
}


// Helper function to check if a file exists
async function fileExists(filepath) {
  try {
    await fs.access(filepath);
    return true;
  } catch (err) {
    return false;
  }
}

main();
```

File Path: Suno Tools/extrctr.js
File Content:

```js
import * as cheerio from 'cheerio';
import axios from 'axios';

async function extractSunoData(url) {
    try {
        const response = await axios.get(url);
        const html = response.data;
        const $ = cheerio.load(html);
        let sunoData = null;


        // Extract SUNO_DATA
        $('script').each((i, script) => {
            const scriptContent = $(script).html();
            if (scriptContent && scriptContent.includes('window.__SUNO_DATA__')) {
                const regex = /window\.__SUNO_DATA__\s*=\s*({.*?});/s;
                const match = regex.exec(scriptContent);
                if (match && match[1]) {
                    try {
                        sunoData = JSON.parse(match[1]);

                        // Stop iterating once data is found
                        return false; // This is how you break out of a cheerio each loop


                    } catch (e) {
                        console.error("Error parsing SUNO_DATA:", e);
                        return false; // Stop in case of parse error
                    }
                }
            }
        });



        if (sunoData) {
            return { jsonData: sunoData }; // Return only the relevant data
        } else {
            return { error: "Could not find window.__SUNO_DATA__" }; // Specific error
        }

    } catch (error) {
        console.error("Error fetching or processing URL:", error);
        return { error: error.message }; // Detailed error message
    }
}

async function main() {
    const sunoUrl = process.argv[2];

    if (!sunoUrl) {
        console.error("Please provide a Suno URL as a command-line argument.");
        return;
    }

    const extractedData = await extractSunoData(sunoUrl);
    console.log(JSON.stringify(extractedData, null, 2)); // Pretty-print JSON

}


main();
```

File Path: Suno Tools/get_suno.py
File Content:

```py
import os
import re
import json
import requests
import argparse
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, USLT, COMM, TXXX, TBPM
import librosa
import platform

def extract_script_content(html):
    pattern = r'<script>\s*self\.__next_f\.push\(\[.*?,"(.*?)"\]\s*\)</script>'
    matches = re.findall(pattern, html, re.DOTALL)
    unified_content = ''.join(matches).replace(r'\"', '"').replace(r'\\n', '\n').replace(r'\\t', '\t')
    # Decode all UTF-8 encoded sequences
    unified_content = unified_content.encode().decode('unicode_escape')
    return unified_content

def extract_json(unified_content):
    # Extract the main JSON block
    main_pattern = r'{"clip":{.*?}}'
    main_match = re.search(main_pattern, unified_content, re.DOTALL)
    if main_match:
        json_str = main_match.group(0)

        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            # Attempt to clean the JSON string and retry
            json_str_cleaned = re.sub(r'[\x00-\x1f\x7f]', '', json_str)
            try:
                json_data = json.loads(json_str_cleaned)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON after cleaning: {e}")
                return None
    else:
        json_data = None

    # Extract the additional JSON-like structures
    additional_pattern = r'\d+:\[\["\$".*?\]\]|\d+:[null,.*?]'
    matches = re.findall(additional_pattern, unified_content, re.DOTALL)

    additional_data = {}
    for match in matches:
        try:
            key, value = match.split(":", 1)
            value = json.loads(value)

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, list) and len(item) == 4:
                        inner_key = item[3].get("name") or item[3].get("property")
                        if inner_key:
                            additional_data[inner_key] = item[3].get("content", '').strip()
                        elif item[2] == "children":
                            additional_data["children"] = item[3].get("children", '').strip()
            elif isinstance(value, dict):
                additional_data.update(value)

        except (json.JSONDecodeError, ValueError):
            continue  # Skip any lines that can't be converted to JSON

    if json_data:
        # Check if 'prompt' is $16, replace it with 'lyrics' value if it exists
        prompt = json_data['clip']['metadata'].get('prompt', '').strip()
        lyrics = extract_lyrics(unified_content)  # Extract the lyrics from the unified content
        if prompt == '$16' and lyrics:
            json_data['clip']['metadata']['prompt'] = lyrics.strip()

        # Strip spaces from all string values in json_data
        def strip_spaces(obj):
            if isinstance(obj, dict):
                return {k: strip_spaces(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [strip_spaces(elem) for elem in obj]
            elif isinstance(obj, str):
                return obj.strip()
            else:
                return obj

        # Apply space stripping to json_data and additional_data
        json_data = strip_spaces(json_data)
        additional_data = strip_spaces(additional_data)

        # Add the additional data at the end of the 'clip' object
        json_data['clip'].update(additional_data)

    return json_data

def extract_lyrics(unified_content):
    # Adjust the pattern to capture any text, including special characters, between '16:T' and '6:["$'
    lyrics_pattern = r'16:T[0-9a-f]+,(.*?)6:\["\$"'

    # Use re.DOTALL to make sure that the pattern matches across multiple lines
    match = re.search(lyrics_pattern, unified_content, re.DOTALL)

    if match:
        lyrics = match.group(1).strip()  # Use .strip() to clean up any leading/trailing whitespace
        return lyrics.replace(r'\\n', '\n').replace(r'\n', '\n')  # Properly format newlines
    return None

def download_file(url, filename):
    response = requests.get(url, timeout=30)
    with open(filename, 'wb') as file:
        file.write(response.content)

def tag_mp3_file(mp3_filename, clip, image_filename, bpm, url):
    audio = EasyID3(mp3_filename)
    audio['title'] = clip['title']
    audio['artist'] = clip['display_name']
    audio['album'] = 'Suno AI Music'
    audio['date'] = clip['created_at'].split('T')[0]
    audio['genre'] = 'SunoAI'
    audio['catalognumber'] = clip['id']
    audio['mood'] = clip['metadata']['tags']
    audio.save()

    audio = ID3(mp3_filename)
    prompt = clip['metadata'].get('prompt', '')

    audio['USLT'] = USLT(encoding=3, lang='eng', desc='', text=prompt.replace('\\n', '\n'))
    formatted_bpm = f"{bpm:.3f}"  # Ensure the BPM is formatted to three decimal places
    audio['TXXX:BPM Precise'] = TXXX(encoding=3, desc='BPM Precise', text=formatted_bpm)

    # Add a comment with Suno URL, Style, and BPM
    comment_text = f"Suno URL: {url}\nStyle: {clip['metadata'].get('tags', 'N/A')}\nBPM: {clip['metadata'].get('estimated_bpm', 'N/A')}"
    audio['COMM'] = COMM(encoding=3, lang='eng', desc='', text=comment_text)

    if 'tags' in clip['metadata']:
        audio['COMM::tags'] = COMM(encoding=3, lang='eng', desc='tags', text=clip['metadata']['tags'])
    if image_filename:
        with open(image_filename, 'rb') as img_file:
            audio['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img_file.read()
            )
    audio.save()

def estimate_bpm(mp3_filename):
    y, sr = librosa.load(mp3_filename)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo) if tempo.ndim == 0 else float(tempo[0])  # Ensure the tempo is a float

def clean_filename(filename):
    # Define illegal characters based on OS
    illegal_chars = {
        'Windows': r'[<>:"/\\|?*]',
        'Linux': r'[\\/\x00]',
        'Darwin': r'[\\/:]',
    }

    os_type = platform.system()  # Get the current OS type
    pattern = illegal_chars.get(os_type, r'[<>:"/\\|?*]')  # Default to Windows pattern

    # Clean the filename by replacing illegal characters with an underscore
    return re.sub(pattern, '_', filename)

def main():
    print(f"{'='*50}\n{' '*15}Suno AI Media Downloader\n{'='*50}\n")
    parser = argparse.ArgumentParser(description="Download media from Suno AI.")
    parser.add_argument("-u", "--url", help="Suno Song URL(s), comma-separated")
    parser.add_argument("-s", "--suno_id", help="Suno Song ID(s), comma-separated")
    parser.add_argument("-a", "--audio", action="store_true", help="Download audio and cover image")
    parser.add_argument("-v", "--video", action="store_true", help="Download video only")
    parser.add_argument("-i", "--image", action="store_true", help="Download image only")
    parser.add_argument("-d", "--data", action="store_true", help="Print JSON data")
    parser.add_argument("-l", "--list", help="Path to a file containing a list of Suno Song URLs")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("-cd", "--change_directory", default="downloads", help="Directory to save downloads, default is 'downloads'")
    parser.add_argument("-sr", "--save_response", action="store_true", help="Save raw response to file")

    args = parser.parse_args()

    # Use the specified directory or default to 'downloads'
    download_dir = args.change_directory

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    urls = []
    if args.list:
        with open(args.list, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
    elif args.url:
        urls.extend(args.url.split(','))
    elif args.suno_id:
        urls.extend([f"https://suno.com/song/{id.strip()}" for id in args.suno_id.split(',')])
    else:
        urls.append(input("Enter Suno Song URL: "))

    for url in urls:
        if not url.strip():
            print("That is not a valid url.")
            continue
        if "suno.com" not in url:
            print("That is not a Suno url.")
            continue

        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            script_content = extract_script_content(response.text)
            json_data = extract_json(script_content)
            if not json_data:
                print(f"Failed to extract JSON data from URL: {url}")
                continue

            clip = json_data['clip']

            # Set the directory for downloads based on clip display name
            final_download_dir = os.path.join(download_dir, clean_filename(clip['display_name']))
            if not os.path.exists(final_download_dir):
                os.makedirs(final_download_dir)

            # Ensure BPM is estimated before setting the filename
            audio_url = clip['audio_url']
            audio_filename_temp = os.path.join(final_download_dir, 'temp_audio.mp3')
            download_file(audio_url, audio_filename_temp)
            bpm = estimate_bpm(audio_filename_temp)
            os.remove(audio_filename_temp)

            # Add the estimated BPM to the metadata
            json_data['clip']['metadata']['estimated_bpm'] = f"{bpm:.3f} BPM"

            base_filename = clean_filename(f"{clip['display_name']} - {clip['title']} {{id-{clip['id']}}}")
            base_filename = re.sub(r'[<>:"/\\|?*]', '', base_filename.replace('\\n', '').replace('\n', ''))

            # Add the Suno song URL to the JSON data
            final_json_data = {"suno_song_url": url, "clip": clip}

            json_filename = os.path.join(final_download_dir, f"{base_filename}.json")
            if not os.path.exists(json_filename) or args.force:
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(final_json_data, json_file, indent=4)
            else:
                print(f"Json Exists - Skipping id: {clip['id']}")

            if args.data:
                print(json.dumps(final_json_data, indent=4))

            # Save raw response if requested
            if args.save_response:
                response_filename = os.path.join(final_download_dir, f"{base_filename}-response.txt")
                with open(response_filename, 'w', encoding='utf-8') as response_file:
                    response_file.write(script_content)

            image_filename = None
            # Ensure image is downloaded when audio is selected
            if args.audio or args.image:
                image_url = clip['image_large_url']
                image_filename = os.path.join(final_download_dir, f"{base_filename}.jpeg")
                if not os.path.exists(image_filename) or args.force:
                    print(f"Downloading {image_url}...")
                    download_file(image_url, image_filename)
                    print(f"    Downloaded: {base_filename}.jpeg\n")
                else:
                    print(f"Image Exists - Skipping id: {clip['id']}")

            if args.audio or args.video:
                if args.audio:
                    audio_filename = os.path.join(final_download_dir, f"{base_filename}.mp3")
                    if not os.path.exists(audio_filename) or args.force:
                        print(f"Downloading {audio_url}...")
                        download_file(audio_url, audio_filename)
                        print(f"    Downloaded: {base_filename}.mp3")
                        print(f"    Detecting BPM for {base_filename}.mp3")
                        print(f"        Estimated BPM: {bpm:.3f}")
                        print(f"    Writing ID3 Tags on: {base_filename}.mp3")
                        tag_mp3_file(audio_filename, clip, image_filename, bpm, url)
                    else:
                        print(f"Audio Exists - Skipping id: {clip['id']}")

                if args.video:
                    video_url = clip['video_url']
                    video_filename = os.path.join(final_download_dir, f"{base_filename}.mp4")
                    if not os.path.exists(video_filename) or args.force:
                        print(f"Downloading {video_url}...")
                        download_file(video_url, video_filename)
                        print(f"    Downloaded: {base_filename}.mp4\n")
                    else:
                        print(f"Video Exists - Skipping id: {clip['id']}")
            else:  # Default behavior without specific args
                image_url = clip['image_large_url']
                image_filename = os.path.join(final_download_dir, f"{base_filename}.jpeg")
                if not os.path.exists(image_filename) or args.force:
                    print(f"Downloading {image_url}...")
                    download_file(image_url, image_filename)
                    print(f"    Downloaded: {base_filename}.jpeg\n")
                else:
                    print(f"Image Exists - Skipping id: {clip['id']}")

                audio_filename = os.path.join(final_download_dir, f"{base_filename}.mp3")
                if not os.path.exists(audio_filename) or args.force:
                    print(f"Downloading {audio_url}...")
                    download_file(audio_url, audio_filename)
                    print(f"    Downloaded: {base_filename}.mp3")
                    print(f"    Detecting BPM for {base_filename}.mp3")
                    print(f"        Estimated BPM: {bpm:.3f}")
                    print(f"    Writing ID3 Tags on: {base_filename}.mp3")
                    tag_mp3_file(audio_filename, clip, image_filename, bpm, url)
                else:
                    print(f"Audio Exists - Skipping id: {clip['id']}")

                video_url = clip['video_url']
                video_filename = os.path.join(final_download_dir, f"{base_filename}.mp4")
                if not os.path.exists(video_filename) or args.force:
                    print(f"Downloading {video_url}...")
                    download_file(video_url, video_filename)
                    print(f"    Downloaded: {base_filename}.mp4\n")
                else:
                    print(f"Video Exists - Skipping id: {clip['id']}")
        else:
            print(f"Failed to fetch the URL: {response.status_code}")

if __name__ == "__main__":
    main()

```

File Path: Suno Tools/index.js
File Content:

```js
import * as fs from 'fs/promises';
import MP3Tag from 'mp3tag.js';
import { parse } from 'node-html-parser';
import path from 'path';

const BASE_PATH = 'C:\\Users\\User\\Documents\\Github\\suno_ai_downloader\\tracks';

async function main() {
  const filePath = 'C://Users//User//Documents//Github//suno_ai_downloader//unique_songs.txt';

  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const urls = fileContent.split(/\s+/).filter(line => line.trim() !== '');

    for (const url of urls) {
      const uuid = url.match(
        /\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b/,
      );

      if (!uuid) {
        console.error('Invalid UUID:', url);
        continue;
      }

      console.log('Processing UUID:', uuid[0]);
      const formattedUrl = `https://suno.com/song/${uuid[0]}`;

      try {
        // Pass the UUID (song ID) along with the URL
        await fetchSongData(formattedUrl, uuid[0]);
      } catch (err) {
        console.error(`Error processing ${formattedUrl}:`, err);
      }
    }
  } catch (err) {
    console.error('Error reading file:', err);
  }
}

// Note: Added a second parameter "songId" to receive the song UUID
async function fetchSongData(url, songId) {
  const result = await fetch(url);
  if (!result.ok) {
    console.error('Failed to fetch:', url);
    return;
  }
  const html = await result.text();
  const root = parse(html);

  let pushedData = '';

  // Loop over all script tags to find the one with the pushed data
  for (const script of root.querySelectorAll('script')) {
    // Check if script tag contains desired data
    if (!script.text.startsWith('self.__next_f.push([')) {
      continue;
    }

    // Extract the data from the script tag using regex
    const data = script.text.match(
      /\s*self\.__next_f.push\(\[\s*1,\s*"(?<wanted>.*)",?\s*\]\);?/m,
    );
    if (data && data[1]) {
      const better = JSON.parse(`"${data[1]}"`);
      pushedData += better;
    }
  }

  // Extract JSON data starting from '{"clip":'
  const start = pushedData.indexOf('{"clip":');
  if (start === -1) {
    console.error('Failed to find clip data in', url);
    return;
  }

  const clip = pushedData.slice(start);
  let json = null;
  let endCut = 0;

  try {
    json = JSON.parse(clip);
  } catch (e) {
    const position = e.message.match(/position (\d+)/);
    if (position) {
      endCut = parseInt(position[1]);
    } else {
      console.error('Failed to parse json:', e);
      return;
    }

    try {
      json = JSON.parse(clip.slice(0, endCut));
    } catch (e) {
      console.error('Failed to parse json again:', e);
      return;
    }
  }

  // Pass the songId down to doSong
  await doSong(json.clip, songId);
}

// Updated doSong function to accept the songId parameter
async function doSong(data, songId) {
  const mp3Buffer = await fetch(data.audio_url).then((res) =>
    res.arrayBuffer(),
  );
  const artBuffer = await fetch(data.image_large_url).then((res) =>
    res.arrayBuffer(),
  );

  const songTitle = data.title;
  const songDirPath = path.join(BASE_PATH, songTitle);
  await fs.mkdir(songDirPath, { recursive: true });

  // Define the base filename (only the song title)
  let baseFilename = songTitle;
  let filename = path.join(songDirPath, `${baseFilename}.mp3`);

  // Check if file exists, and use Roman numerals for duplicates
  filename = await getUniqueFilenameRoman(filename, songDirPath, baseFilename);

  // Apply metadata to MP3 using MP3Tag.js
  const tag = new MP3Tag(Buffer.from(mp3Buffer));
  tag.read();
  tag.tags.title = songTitle;          // Use only song title
  tag.tags.artist = data.display_name;
  tag.tags.album = songTitle;          // Set album tag
  tag.tags.genre = data.metadata.tags;
  // Here we incorporate the song ID into the comment tag for later duplicate filtering.
  tag.tags.comment = `Suno AI (Song ID: ${songId})`;
  tag.tags.year = new Date(data.created_at).getFullYear().toString();
  tag.tags.v2.APIC = [
    {
      format: 'image/jpeg',
      type: 0,
      description: 'Suno AI',
      data: Buffer.from(artBuffer),
    },
  ];

  // Alternatively, if you prefer to store the song ID in a custom tag (e.g., TXXX),
  // you could uncomment the following block (provided MP3Tag.js supports it):
  /*
  tag.tags.v2.TXXX = [
    {
      description: 'Song ID',
      data: songId,
    },
  ];
  */

  // Save the MP3 file
  await fs.writeFile(
    filename,
    Buffer.from(
      tag.save({
        strict: true, // Strict mode, validates all inputs against the standards.
        id3v2: { padding: 4096 },
      }),
    ),
  );

  if (tag.error) {
    console.error('MP3Tag error:', tag.error);
  } else {
    console.log('Wrote:', filename);
  }
}

// Function to get a unique filename using Roman numerals
async function getUniqueFilenameRoman(filepath, dir, baseFilename) {
  let ext = path.extname(filepath);
  let filename = path.basename(filepath, ext);
  let counter = 0; // Start at 0, first instance will be without Roman Numeral
  let newFilename = path.join(dir, `${baseFilename}${ext}`);

  while (await fileExists(newFilename)) {
    counter++;
    const roman = toRoman(counter);
    newFilename = path.join(dir, `${baseFilename} ${roman}${ext}`);
  }

  return newFilename;
}

// Helper function to convert numbers to Roman numerals
function toRoman(num) {
  const romanMap = {
    1: 'I',
    4: 'IV',
    5: 'V',
    9: 'IX',
    10: 'X',
    40: 'XL',
    50: 'L',
    90: 'XC',
    100: 'C',
    400: 'CD',
    500: 'D',
    900: 'CM',
    1000: 'M',
  };

  let result = '';
  const decimalValues = Object.keys(romanMap)
    .map(Number)
    .sort((a, b) => b - a);

  for (const decimal of decimalValues) {
    while (num >= decimal) {
      result += romanMap[decimal];
      num -= decimal;
    }
  }

  return result;
}

// Helper function to check if a file exists
async function fileExists(filepath) {
  try {
    await fs.access(filepath);
    return true;
  } catch (err) {
    return false;
  }
}

main();

```

File Path: Suno Tools/info.js
File Content:

```js
import * as fs from 'fs/promises';
import fetch from 'node-fetch';
import { parse } from 'node-html-parser';
// Removed 'path' import since it's not used

async function fetchPageContent(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch page: ${response.statusText}`);
    }
    const html = await response.text();
    return html;
}

function extractScriptTags(html) {
    const root = parse(html);
    const scriptTags = root.querySelectorAll('script');
    return scriptTags;
}

function findDataScripts(scriptTags) {
    return scriptTags.filter(script => script.text.includes('self.__next_f.push'));
}

function extractDataFromScripts(dataScripts) {
    let concatenatedData = '';
    let lyricsData = '';

    for (const script of dataScripts) {
        const match = script.text.match(/self\.__next_f\.push\(\[\d+,"(.*)"\]\)/s);
        if (match && match[1]) {
            // Unescape the string
            const unescapedString = JSON.parse(`"${match[1]}"`);
            // Check if the string contains JSON data
            if (unescapedString.trim().startsWith('{"clip":')) {
                concatenatedData += unescapedString;
            } else {
                // Collect lyrics or other text content
                lyricsData += unescapedString + '\n';
            }
        }
    }

    return { concatenatedData, lyricsData };
}

function extractJsonData(concatenatedData) {
    const jsonStartIndex = concatenatedData.indexOf('{"clip":');
    if (jsonStartIndex === -1) {
        throw new Error('JSON data not found in concatenated string.');
    }

    const jsonString = concatenatedData.slice(jsonStartIndex);

    let jsonData;
    try {
        jsonData = JSON.parse(jsonString);
    } catch (error) {
        const positionMatch = error.message.match(/at position (\d+)/);
        if (positionMatch) {
            const validJsonSubstring = jsonString.slice(0, parseInt(positionMatch[1]));
            jsonData = JSON.parse(validJsonSubstring);
        } else {
            throw new Error('Failed to parse JSON data.');
        }
    }

    return jsonData;
}

function extractSongInformation(jsonData) {
    const clip = jsonData.clip;

    const title = clip.title || 'Unknown Title';
    const artist = clip.display_name || 'Unknown Artist';
    const coverImageUrl = clip.image_large_url || clip.image_url || 'No Image URL';
    const creationDate = clip.created_at || 'Unknown Date';
    const audioUrl = clip.audio_url || 'No Audio URL';
    const tags = clip.metadata.tags || 'No Tags';

    return {
        title,
        artist,
        coverImageUrl,
        creationDate,
        audioUrl,
        tags,
    };
}

function sanitizeFileName(name) {
    return name.replace(/[<>:"/\\|?*]/g, '-');
}

async function saveSongDetailsAsMarkdown(details) {
    const {
        title,
        artist,
        tags,
        lyrics,
        coverImageUrl,
        creationDate,
        audioUrl,
    } = details;

    const markdownContent = `
# ${title}

![Cover Image](${coverImageUrl})

**Artist:** ${artist}
**Tags:** ${tags}
**Release Date:** ${creationDate}
**Listen:** [MP3 Link](${audioUrl})

## Lyrics:
${lyrics}
`;

    const sanitizedArtist = sanitizeFileName(artist);
    const sanitizedTitle = sanitizeFileName(title);
    const markdownFilename = `songs/${sanitizedArtist} - ${sanitizedTitle}.md`;

    await fs.writeFile(markdownFilename, markdownContent);
    console.log(`Saved markdown: ${markdownFilename}`);
}

// Only one definition of processURL
async function processURL(url) {
    try {
        const html = await fetchPageContent(url);
        const scriptTags = extractScriptTags(html);
        const dataScripts = findDataScripts(scriptTags);
        const { concatenatedData, lyricsData } = extractDataFromScripts(dataScripts);
        const jsonData = extractJsonData(concatenatedData);
        const songDetails = extractSongInformation(jsonData);
        songDetails.lyrics = lyricsData.trim() || 'Lyrics not available';

        // Save the song details as markdown
        await saveSongDetailsAsMarkdown(songDetails);
    } catch (error) {
        console.error(`An unexpected error occurred while processing ${url}:`, error);
    }
}

// Get the URL from the command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Please provide a Suno URL as an argument');
    process.exit(1);
}

const songUrl = args[0];
processURL(songUrl);

```

File Path: Suno Tools/main.py
File Content:

```py
import os
import requests
from bs4 import BeautifulSoup


def get_song_title(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        heading_tag = soup.select_one('.chakra-heading')
        if heading_tag:
            song_title = heading_tag.text.strip()
            return song_title
        else:
            print("No song title found.")
            return None
    except Exception as e:
        print(f"Error while parsing HTML: {e}")
        return None


def download_song_from_page(song_page_url, save_dir="music"):
    try:
        if not song_page_url.startswith("https://suno.com/song/"):
            raise ValueError(
                "Incorrect URL. It should start with 'https://suno.com/song/'")

        song_id = song_page_url.split('/')[-1]
        song_page_title = f"https://suno.com/embed/{song_id}"
        response_title = requests.get(song_page_title)
        if response_title.status_code != 200:
            print(f"Error: {response.status_code}")
            return

        html = response_title.text
        song_title = get_song_title(html)
        if not song_title:
            return

        song_url = f"https://cdn1.suno.ai/{song_id}.mp3"

        file_name = f"{song_title}.mp3"
        file_path = os.path.join(save_dir, file_name)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        response = requests.get(song_url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"{file_name} downloaded in {file_path}")
        else:
            print(f"Download error {file_name}: {response.status_code}")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"There's been an error: {e}")


if __name__ == "__main__":
    print("Software for downloading music from suno.com")
    print("Go to suno.com, pick a song you like, go to the song page and copy the link.")
    print("Example link: https://suno.com/song/eaba4d6e-f7ab-4bc4-a48b-6e2c8d859dbc")
    print("Paste the link at the bottom and press Enter.")
    while True:
        song_page_url = input(f"\nEnter a link to the song's page: ")
        download_song_from_page(song_page_url)
        if (input("Would you like to continue? (y/n): ") == "n"):
            break

```

File Path: Suno Tools/suno-ai-downloader/getData.js
File Content:

```js
// Login to https://suno.com/me
copy(
  [
    "song_name,song_url,song_prompt",
    ...[
      ...$('[role="grid"]')[
        Object.keys($('[role="grid"]')).filter((x) =>
          x.startsWith("__reactProps")
        )[0]
      ].children[0].props.values[0][1].collection,
    ]
      .filter((x) => x.value.audio_url)
      .map((x) => {
        const title = x.value.title.trim() || x.value.id;
        // Use a hash of the song's ID for consistency
        const hash = x.value.id.slice(0, 5); // Use the first 5 characters of the ID
        // Get UUID from the song's ID
        const uuid = x.value.id;
        // Format filename: lowercase, replace spaces with dashes, add id and hash
        const formattedTitle = `${title
          .toLowerCase()
          .replace(/\s+/g, "-")}-id-${hash}`;

        // Find the description from the DOM using the song ID
        const songElement = document.querySelector(
          `[data-clip-id="${x.value.id}"]`
        );
        let description = "";
        if (songElement) {
          const descriptionSpan = Array.from(
            songElement.querySelectorAll("span[title]")
          ).find((span) => span.textContent.trim().length > 50);
          description = descriptionSpan
            ? descriptionSpan.getAttribute("title").trim()
            : "No description available";
        }

        // Include original UUID filename in the description
        const fullDescription = `Original filename: ${uuid}.mp3\n\nPrompt:\n${description}`;

        // Always wrap description in quotes for consistency, and ensure no trailing newline
        return `${formattedTitle}.mp3,${
          x.value.audio_url
        },"${fullDescription.replace(/\n$/, "")}"`;
      }),
  ]
    .join("\n")
    .trim() // Trim any extra whitespace/newlines from the final output
);

```

File Path: Suno Tools/suno-ai-downloader/README.md
File Content:

```md
# Suno Music Downloader

A set of tools to download your music from Suno.ai with organized filenames and prompts.

## Setup

1. Clone this repository
2. Install Python requirements:
   ```bash
   pip3 install -r requirements.txt
   ```

# Usage

## 1. Get Song Data

1. Login to https://suno.com/me
2. Open browser developer tools (F12)
3. Copy and paste the contents of `getData.js` into the console
4. Copy the output and save it to `songs.csv`

The script will generate a CSV with:
- Formatted filenames (with random ID)
- Download URLs
- Original prompts and UUIDs

## 2. Download Songs

Run the Python downloader:

```bash
python3 suno-downloader.py
```

## Features

- **Fast Parallel Downloads**: Downloads 4 files simultaneously
- **Smart File Handling**:
  - Skips existing files automatically
  - Creates organized filenames with IDs
  - Preserves original UUIDs in text files
- **Progress Tracking**:
  - Real-time progress bars for each download
  - Download speed and size information
  - Completion summary with success/failure counts
- **Error Handling**:
  - Automatic retry on failed downloads (up to 3 attempts)
  - Detailed error reporting
  - Graceful handling of network issues

# Output Structure

```
songs/
  ├── song-name-id-xxxxx.mp3  # Organized filename with random ID
  └── song-name-id-xxxxx.txt  # Matching text file with prompt
```

Text files contain:

```
Original filename: uuid.mp3

Prompt:
Your original generation prompt
```

# Files

- `getData.js` - Browser script to extract song data
- `suno-downloader.py` - Python script with parallel download capability
- `requirements.txt` - Python package dependencies
- `songs.csv` - Generated list of songs to download

# Technical Details

- Uses Python's ThreadPoolExecutor for parallel downloads
- Configurable number of simultaneous downloads (default: 4)
- Progress bars powered by tqdm
- Robust error handling with automatic retries

```
File Path: Suno Tools/suno-ai-downloader/requirements.txt
File Content:
```txt
tqdm>=4.65.0
requests>=2.31.0

```

File Path: Suno Tools/suno-ai-downloader/suno-downloader.py
File Content:

```py
#!/usr/bin/env python3

import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
from pathlib import Path
import sys

MAX_RETRIES = 3
MAX_WORKERS = 4


def download_file(url, filename, total_size=None):
    """Download a file with progress bar and retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total = total_size or int(response.headers.get("content-length", 0))

            with open(filename, "wb") as f, tqdm(
                desc=Path(filename).name,
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)
            return True

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"\nRetrying {filename} (Attempt {attempt + 2}/{MAX_RETRIES})")
                time.sleep(2)
            else:
                print(f"\nFailed to download {filename}: {str(e)}")
                return False


def process_song(row):
    """Process a single song (for parallel processing)."""
    try:
        # Skip empty or malformed rows
        if not row or len(row) != 3:
            print(f"Skipping invalid row: {row}")
            return False

        filename, url, description = row

        # Skip if any required field is empty
        if not all([filename.strip(), url.strip(), description.strip()]):
            print(f"Skipping row with empty fields: {filename}")
            return False

        # Create full paths
        mp3_path = os.path.join("songs", filename)
        txt_path = os.path.join("songs", filename.replace(".mp3", ".txt"))

        # Skip if files already exist
        if os.path.exists(mp3_path) and os.path.exists(txt_path):
            print(f"Skipping existing file: {filename}")
            return True

        # Save description to text file
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(description.strip())

        # Download MP3
        return download_file(url, mp3_path)
    except Exception as e:
        print(
            f"Error processing song {filename if 'filename' in locals() else 'unknown'}: {str(e)}"
        )
        return False


def main():
    """Main execution function."""
    # Create songs directory if it doesn't exist
    os.makedirs("songs", exist_ok=True)

    # Read the CSV file
    try:
        with open("songs.csv", "r", encoding="utf-8") as file:
            # Use csv.reader with proper quoting and filtering
            reader = csv.reader(file, quoting=csv.QUOTE_ALL, skipinitialspace=True)
            next(reader)  # Skip header
            # Filter out empty rows and validate row length
            songs = [row for row in reader if row and len(row) == 3]
    except FileNotFoundError:
        print("Error: songs.csv not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        sys.exit(1)

    if not songs:
        print("No valid songs found in CSV")
        sys.exit(1)

    print(f"Found {len(songs)} valid songs to process")

    # Process songs in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_song, songs))

    # Summary
    successful = sum(1 for r in results if r is True)
    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {successful}/{len(songs)} songs")
    if successful != len(songs):
        print(f"Failed downloads: {len(songs) - successful}")


if __name__ == "__main__":
    main()

```

File Path: Suno Tools/suno.js
File Content:

```js
import * as fs from 'fs/promises';
import { parse } from 'node-html-parser';
import fetch from 'node-fetch';
import * as cheerio from 'cheerio'; // Use named import for cheerio
import path from 'path';

// Function to save song details as a markdown file
async function saveSongDetailsAsMarkdown(title, artist, tags, lyrics, coverImageUrl) {
    const markdownContent = `
# ${title}

### Artist: ${artist}
### Tags: ${tags}
### Release Year: ${new Date().getFullYear()}  <!-- Assuming current year, adjust if needed -->

## Lyrics:
${lyrics}

![Cover Image](${coverImageUrl})

_Saved from Suno AI_
    `;

    const sanitizedTitle = title.replace(/[<>:"/\\|?*]+/g, '');
    const sanitizedArtist = artist.replace(/[<>:"/\\|?*]+/g, '');
    const markdownFilename = path.join('songs', `${sanitizedArtist} - ${sanitizedTitle}.md`);

    await fs.mkdir('songs', { recursive: true });
    await fs.writeFile(markdownFilename, markdownContent);
    console.log(`Saved markdown: ${markdownFilename}`);
}

// Function to process a Suno URL and extract metadata (without downloading the song)
async function processURL(url) {
    try {
        const uuid = url.match(/\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b/)[0];
        const sunoURL = `https://suno.com/song/${uuid}`;
        const result = await fetch(sunoURL);

        if (!result.ok) {
            console.error('Failed to fetch:', sunoURL);
            return;
        }

        const html = await result.text();
        const $ = cheerio.load(html);

        // Extract the title (update the selector to match the actual page structure)
        const title = $('h1').text().trim() || 'Unknown Title';

        // Extract the artist (update selector to match actual artist container)
        const artist = $('.artist-name').text().trim() || 'Unknown Artist';

        // Extract the tags (update the selector if needed)
        const tags = $('.tags').text().trim() || 'No Tags';

        // Extract the lyrics (update selector to match the actual lyrics container)
        const lyrics = $('.lyrics').text().trim() || 'No Lyrics';

        // Extract cover image URL (update the selector as needed)
        const coverImageUrl = $('img.cover').attr('src') || '';

        // Save the extracted details as a markdown file
        await saveSongDetailsAsMarkdown(title, artist, tags, lyrics, coverImageUrl);
    } catch (error) {
        console.error(`An error occurred while processing ${url}:`, error);
    }
}

// Main function to handle multiple URLs
async function main() {
    const urls = process.argv.slice(2);

    if (!urls.length) {
        console.error('Please provide at least one Suno URL.');
        process.exit(1);
    }

    for (const url of urls) {
        if (!url.startsWith('https://suno.com/song/')) {
            console.warn(`Skipping invalid URL: ${url}`);
            continue;
        }
        await processURL(url);
    }
}

main();
```

File Path: Suno Tools/suno.py
File Content:

```py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import argparse
from urllib.parse import urljoin
import time

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def scrape_data(url, session):
    logging.info(f"Scraping URL: {url}")
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Define the selectors
    selectors = {
        "Title": "div.animate-marquee > a.whitespace-nowrap.mr-24",
        "Tags": ".md\\:mt-4 .font-sans.break-all.text-sm.text-primary.mr-1",
        "Metadata": "span.text-secondary.text-sm.font-sans",
        "Lyrics": "textarea[readonly]",
        "Cover": "img.absolute.inset-0.w-full.h-full.object-cover",
        "Link": "div.animate-marquee > a.whitespace-nowrap.mr-24"
    }

    data = {}

    # Extract Title
    title_element = soup.select_one(selectors['Title'])
    data['Title'] = title_element.get_text(
        strip=True) if title_element else None

    # Extract Tags
    tag_elements = soup.select(selectors['Tags'])
    data['Tags'] = ', '.join([tag.get_text(strip=True)
                             for tag in tag_elements]) if tag_elements else None

    # Extract Metadata
    metadata_elements = soup.select(selectors['Metadata'])
    data['Metadata'] = ', '.join([meta.get_text(
        strip=True) for meta in metadata_elements]) if metadata_elements else None

    # Extract Lyrics
    lyrics_element = soup.select_one(selectors['Lyrics'])
    data['Lyrics'] = lyrics_element.get_text(
        strip=True) if lyrics_element else None

    # Extract Cover image URL
    cover_element = soup.select_one(selectors['Cover'])
    if cover_element and cover_element.has_attr('src'):
        data['Cover'] = urljoin(url, cover_element['src'])
    else:
        data['Cover'] = None

    # Extract Link
    link_element = soup.select_one(selectors['Link'])
    if link_element and link_element.has_attr('href'):
        data['Link'] = urljoin(url, link_element['href'])
    else:
        data['Link'] = None

    return data


def main(input_file, output_file):
    # Read URLs from the input file
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        logging.error("No URLs found in the input file.")
        return

    # Initialize a session
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)'})

    # Scrape data from all URLs
    scraped_data = []
    for url in urls:
        data = scrape_data(url, session)
        if data:
            scraped_data.append(data)
        time.sleep(1)  # Polite crawling by adding a delay between requests

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(scraped_data)
    df.to_csv(output_file, index=False)

    logging.info(f"Data scraped and saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape data from URLs and save to CSV.")
    parser.add_argument('--input', required=True,
                        help="Input file containing URLs")
    parser.add_argument(
        '--output', default='scraped_data.csv', help="Output CSV file")

    args = parser.parse_args()

    main(args.input, args.output)

```

File Path: Suno Tools/suno_downloader.py
File Content:

```py
from playwright.sync_api import sync_playwright
import os
import re
import requests
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, USLT, APIC, ID3NoHeaderError

# Ensure the Logs folder exists.
os.makedirs("Logs", exist_ok=True)

# Global variables for timeouts (in milliseconds) – will be set in main().
NAV_TIMEOUT = 60000       # default: 60 seconds (will be updated)
SELECTOR_TIMEOUT = 20000  # default: 20 seconds (will be updated)

# Global log file (inside Logs folder relative to script location) and a dictionary for failure details.
LOG_FILE = os.path.join("Logs", "suno_operation_log.txt")
failures = {}  # Stores detailed failure messages per URL.

# Ensure the 'Logs' directory exists
if not os.path.exists('Logs'):
    os.makedirs('Logs')

# Global flag for overwriting files (set by the user at the start).
OVERWRITE_FILES = False

def log_operation(message):
    """Appends a message to the operation log file and prints it."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def initialize_files(skip_file, failed_file):
    """
    Ensures that the skip and failed files exist.
    If they do not exist, they are created with an initial header.
    """
    if not os.path.exists(skip_file):
        with open(skip_file, "w", encoding="utf-8") as f:
            f.write("Suno URLs SKIPPED:\n")
        log_operation(f"Created skip file: {skip_file}")
    if not os.path.exists(failed_file):
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write("Suno URLs FAILED:\n")
        log_operation(f"Created failed file: {failed_file}")

def read_urls_from_file(file_path):
    """Reads URLs from a file, ignoring empty lines."""
    if not os.path.exists(file_path):
        log_operation(f"❌ File not found: {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def sanitize_filename(filename):
    """Replaces illegal filename characters with an underscore."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def record_failure(url, message):
    """Records a failure message for a given URL in the global dictionary and logs it."""
    if url not in failures:
        failures[url] = []
    failures[url].append(message)
    log_operation(f"[{url}] FAILURE: {message}")

def extract_gpt_prompt(html):
    """
    Attempts to extract the GPT prompt from the HTML source.
    Searches for a JSON fragment with "gpt_description_prompt" (removing the trailing phrase)
    and falls back to the 3rd <meta> tag with a content attribute.
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        script_text = script.get_text()
        if "gpt_description_prompt" in script_text:
            match = re.search(r'"gpt_description_prompt"\s*:\s*\\"?([^\\"]+)\\"?', script_text)
            if match:
                prompt = match.group(1).strip()
                prompt = prompt.replace(" song. Listen and make your own with Suno.", "").strip()
                if prompt:
                    return prompt
    meta_tags = soup.find_all("meta", attrs={"content": True})
    if len(meta_tags) >= 3:
        fallback_prompt = meta_tags[2].get("content", "").strip()
        fallback_prompt = fallback_prompt.replace(" song. Listen and make your own with Suno.", "").strip()
        if fallback_prompt:
            return fallback_prompt
    return None

def extract_page_data(url):
    """
    Uses Playwright to load the page at the given URL and extract:
      - The page title (for filenames)
      - The lyrics text (using the CSS selector "section.w-full > div:nth-child(1)")
      - The full HTML content
      - The GPT prompt (via extract_gpt_prompt)
    Timeouts for navigation and selectors are set by the global variables.
    """
    global NAV_TIMEOUT, SELECTOR_TIMEOUT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        log_operation(f"⏳ Navigating to {url}...")
        try:
            page.goto(url, timeout=NAV_TIMEOUT)
        except Exception as e:
            msg = f"Error navigating to {url}: {e}"
            log_operation(f"❌ {msg}")
            record_failure(url, msg)
            browser.close()
            return "Unknown_Song", None, None, None
        try:
            page.wait_for_selector("section.w-full > div:nth-child(1)", timeout=SELECTOR_TIMEOUT)
            lyrics = page.text_content("section.w-full > div:nth-child(1)").strip()
        except Exception as e:
            msg = f"Error extracting lyrics from {url}: {e}"
            log_operation(f"❌ {msg}")
            record_failure(url, msg)
            lyrics = None
        title = page.title() or "Unknown_Song"
        html_content = page.content()
        gpt_prompt = extract_gpt_prompt(html_content)
        if not gpt_prompt:
            record_failure(url, "GPT prompt not found")
        browser.close()
        return title, lyrics, gpt_prompt, html_content

def save_text_to_file(text, directory, filename):
    """
    Saves the given text to a file in the specified directory.
    If OVERWRITE_FILES is False and the file exists, appends a number.
    """
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    if not OVERWRITE_FILES:
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(directory, f"{base} ({counter}){ext}")
            counter += 1
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    log_operation(f"✅ Saved to {filepath}")

def download_file(url, directory, filename, extension):
    """
    Downloads a file from the provided URL using Requests and saves it
    in the specified directory with the given filename and extension.
    If OVERWRITE_FILES is False and the file exists, appends a number.
    Returns the final file path on success, or None on failure.
    """
    if not url:
        msg = f"URL not provided for {filename}.{extension}"
        log_operation(f"⚠️ {msg}")
        return None
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.{extension}")
    if not OVERWRITE_FILES:
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(directory, f"{filename} ({counter}).{extension}")
            counter += 1
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        log_operation(f"✅ Downloaded file to {filepath}")
        return filepath
    except Exception as e:
        msg = f"Failed to download {url}: {e}"
        log_operation(f"❌ {msg}")
        record_failure("", msg)
        return None

def add_lyrics_to_mp3(mp3_filepath, lyrics):
    """
    Adds the provided lyrics to the MP3 file's ID3 tag (USLT frame).
    Overwrites any existing lyrics.
    """
    try:
        try:
            audio = ID3(mp3_filepath)
        except ID3NoHeaderError:
            audio = ID3()
        audio.delall("USLT")
        audio.add(USLT(encoding=3, desc=u"lyrics", text=lyrics))
        audio.save(mp3_filepath)
        log_operation(f"✅ Added lyrics to MP3 tag for {mp3_filepath}")
    except Exception as e:
        msg = f"Error adding lyrics to MP3 tag for {mp3_filepath}: {e}"
        log_operation(f"❌ {msg}")
        record_failure("", msg)

def add_image_to_mp3(mp3_filepath, image_filepath):
    """
    Embeds the image (from image_filepath) into the MP3 file's ID3 tag (APIC frame).
    Overwrites any existing album art.
    """
    try:
        try:
            audio = ID3(mp3_filepath)
        except ID3NoHeaderError:
            audio = ID3()
        with open(image_filepath, "rb") as img:
            img_data = img.read()
        audio.delall("APIC")
        audio.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=img_data
        ))
        audio.save(mp3_filepath)
        log_operation(f"✅ Embedded image into MP3 tag for {mp3_filepath}")
    except Exception as e:
        msg = f"Error embedding image into MP3 tag for {mp3_filepath}: {e}"
        log_operation(f"❌ {msg}")
        record_failure("", msg)

session = requests.Session()

def get_user_selection():
    """
    Prompts the user to select what to extract and save for each URL.
    Options:
      1. HTML
      2. MP4
      3. MP3
      4. Lyrics
      5. Prompt
      6. Image
      7. Add index (prefix filenames with a padded 5-digit number)
      8. All of 1-6 (extraction options only)
      9. All of 1-7 (extraction options plus indexing)
    """
    print("Select what to extract and save for each URL:")
    print("1. HTML")
    print("2. MP4")
    print("3. MP3")
    print("4. Lyrics")
    print("5. Prompt")
    print("6. Image")
    print("7. Add index (prefix filenames with a padded 5-digit number)")
    print("8. All of 1-6 (extraction options only)")
    print("9. All of 1-7 (extraction options plus indexing)")
    choices = input("Enter numbers separated by commas (e.g., 1,2,4,5,6): ")
    selections = [x.strip() for x in choices.split(",")]
    sel = {
        "html": False,
        "mp4": False,
        "mp3": False,
        "lyrics": False,
        "prompt": False,
        "image": False,
        "index": False
    }
    if "8" in selections:
        sel["html"] = sel["mp4"] = sel["mp3"] = sel["lyrics"] = sel["prompt"] = sel["image"] = True
    if "9" in selections:
        sel["html"] = sel["mp4"] = sel["mp3"] = sel["lyrics"] = sel["prompt"] = sel["image"] = True
        sel["index"] = True
    if "1" in selections: sel["html"] = True
    if "2" in selections: sel["mp4"] = True
    if "3" in selections: sel["mp3"] = True
    if "4" in selections: sel["lyrics"] = True
    if "5" in selections: sel["prompt"] = True
    if "6" in selections: sel["image"] = True
    if "7" in selections: sel["index"] = True
    return sel

def retry_failed_urls(failed_urls, options):
    """Retries processing for the URLs in failed_urls once."""
    if not failed_urls:
        log_operation("✅ No failed URLs to retry.")
        return
    log_operation("\n🔄 Retrying failed URLs...")
    still_failed = set()
    for url in failed_urls:
        log_operation(f"🔄 Retrying URL: {url}")
        title, lyrics, gpt_prompt, html_content = extract_page_data(url)
        sanitized_title = sanitize_filename(title)
        if options["html"]:
            if html_content:
                save_text_to_file(html_content, "HTML", f"{sanitized_title} - Parsed.html")
            else:
                msg = "HTML content not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
        if options["lyrics"]:
            if lyrics:
                save_text_to_file(lyrics, "Lyrics", f"{sanitized_title} - Lyrics.txt")
            else:
                msg = "Lyrics not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
        if options["prompt"]:
            if gpt_prompt:
                save_text_to_file(gpt_prompt, "Prompts", f"{sanitized_title} - Prompt.txt")
            else:
                msg = "GPT prompt not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            msg = f"Error fetching full HTML for media extraction on retry: {e}"
            log_operation(f"❌ {msg}")
            record_failure(url, msg)
            still_failed.add(url)
            continue
        if options["mp4"]:
            video_meta = soup.find("meta", {"property": "og:video:url"})
            video_url = video_meta.get("content") if video_meta else None
            if video_url:
                if not download_file(video_url, "Videos", sanitized_title, "mp4"):
                    still_failed.add(url)
            else:
                msg = "Video URL not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
        if options["mp3"]:
            audio_meta = soup.find("meta", {"property": "og:audio"})
            audio_url = audio_meta.get("content") if audio_meta else None
            if audio_url:
                mp3_filepath = download_file(audio_url, "Audio", sanitized_title, "mp3")
                if not mp3_filepath:
                    still_failed.add(url)
                else:
                    if lyrics:
                        add_lyrics_to_mp3(mp3_filepath, lyrics)
            else:
                msg = "Audio URL not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
        if options["image"]:
            image_meta = soup.find("meta", {"name": "twitter:image"})
            if image_meta:
                img_url = image_meta.get("content")
                if "image_large_" not in img_url:
                    image_meta = soup.find("meta", {"property": "og:image"})
                    img_url = image_meta.get("content") if image_meta else None
            else:
                image_meta = soup.find("meta", {"property": "og:image"})
                img_url = image_meta.get("content") if image_meta else None
            if img_url:
                image_filepath = download_file(img_url, "Images", sanitized_title + " - Art", "jpeg")
                if not image_filepath:
                    still_failed.add(url)
            else:
                msg = "Image URL not found on retry"
                log_operation(f"⚠️ {msg}")
                record_failure(url, msg)
                still_failed.add(url)
    if still_failed:
        log_operation("\n❌ The following URLs still failed after retry:")
        for url in still_failed:
            log_operation(url)
        with open("suno_urls_FAILED.txt", "a", encoding="utf-8") as f:
            f.write("Final failure details for this run:\n")
            for url in still_failed:
                f.write(url + "\n")
    else:
        log_operation("\n✅ All previously failed URLs succeeded on retry.")

def main():
    # Files for URLs and tracking.
    urls_file = "suno_urls.txt"             # File with URLs (one per line)
    skip_file = "suno_urls_SKIPPED.txt"       # File to keep track of processed URLs
    failed_file = "suno_urls_FAILED.txt"      # File to store failure details

    # Ensure that the skip and failed files exist.
    initialize_files(skip_file, failed_file)

    # Prompt the user whether to overwrite files.
    overwrite_choice = input("Do you want to overwrite files if they already exist? (Y/N): ").strip().upper()
    global OVERWRITE_FILES
    if overwrite_choice == "Y":
        OVERWRITE_FILES = True
        log_operation("Files will be overwritten if they exist.")
    else:
        OVERWRITE_FILES = False
        log_operation("Files will not be overwritten; duplicates will have appended numbers.")

    # Read already processed URLs.
    downloaded_set = set()
    if os.path.exists(skip_file):
        with open(skip_file, "r", encoding="utf-8") as f:
            for line in f:
                downloaded_set.add(line.strip())

    options = get_user_selection()

    # Prompt for timeouts (in seconds), then convert to milliseconds.
    try:
        nav_timeout_input = input("Enter timeout1 in seconds for page navigation: (Default 60)")
        nav_timeout_seconds = float(nav_timeout_input)
    except Exception:
        nav_timeout_seconds = 60
    try:
        selector_timeout_input = input("Enter timeout2 in seconds for waiting for selectors: (Default 20)")
        selector_timeout_seconds = float(selector_timeout_input)
    except Exception:
        selector_timeout_seconds = 20
    global NAV_TIMEOUT, SELECTOR_TIMEOUT
    NAV_TIMEOUT = int(nav_timeout_seconds * 1000)
    SELECTOR_TIMEOUT = int(selector_timeout_seconds * 1000)
    log_operation(f"Timeout settings: Navigation = {NAV_TIMEOUT} ms, Selector = {SELECTOR_TIMEOUT} ms")

    if options["index"]:
        current_index = len(downloaded_set)
    else:
        current_index = None

    urls = read_urls_from_file(urls_file)
    if not urls:
        log_operation("❌ No URLs found in the file.")
        return

    failed_urls = set()

    for url in urls:
        if url in downloaded_set:
            log_operation(f"Skipping URL (already processed): {url}")
            continue

        log_operation(f"🔄 Processing URL: {url}")
        if options["index"]:
            current_index += 1
            index_prefix = f"{current_index:05d} - "
        else:
            index_prefix = ""

        title, lyrics, gpt_prompt, html_content = extract_page_data(url)
        sanitized_title = sanitize_filename(title)

        if options["html"]:
            if html_content:
                save_text_to_file(html_content, "HTML", f"{index_prefix}{sanitized_title} - Parsed.html")
            else:
                record_failure(url, "HTML content not found")
                failed_urls.add(url)

        if options["lyrics"]:
            if lyrics:
                save_text_to_file(lyrics, "Lyrics", f"{index_prefix}{sanitized_title} - Lyrics.txt")
            else:
                record_failure(url, "Lyrics not found")
                failed_urls.add(url)

        if options["prompt"]:
            if gpt_prompt:
                save_text_to_file(gpt_prompt, "Prompts", f"{index_prefix}{sanitized_title} - Prompt.txt")
            else:
                record_failure(url, "GPT prompt not found")
                failed_urls.add(url)

        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            record_failure(url, f"Error fetching full HTML for media extraction: {e}")
            failed_urls.add(url)
            continue

        # MP4 extraction block added here.
        if options["mp4"]:
            video_meta = soup.find("meta", {"property": "og:video:url"})
            video_url = video_meta.get("content") if video_meta else None
            if video_url:
                video_filepath = download_file(video_url, "Videos", f"{index_prefix}{sanitized_title}", "mp4")
                if not video_filepath:
                    record_failure(url, "Failed to download video")
                    failed_urls.add(url)
            else:
                record_failure(url, "Video URL not found")
                failed_urls.add(url)

        # MP3 extraction
        current_mp3_filepath = None
        if options["mp3"]:
            audio_meta = soup.find("meta", {"property": "og:audio"})
            audio_url = audio_meta.get("content") if audio_meta else None
            if audio_url:
                current_mp3_filepath = download_file(audio_url, "Audio", f"{index_prefix}{sanitized_title}", "mp3")
                if not current_mp3_filepath:
                    failed_urls.add(url)
                else:
                    if lyrics:
                        add_lyrics_to_mp3(current_mp3_filepath, lyrics)
            else:
                record_failure(url, "Audio URL not found")
                failed_urls.add(url)

        # Image extraction
        current_image_filepath = None
        if options["image"]:
            image_meta = soup.find("meta", {"name": "twitter:image"})
            if image_meta:
                img_url = image_meta.get("content")
                if "image_large_" not in img_url:
                    image_meta = soup.find("meta", {"property": "og:image"})
                    img_url = image_meta.get("content") if image_meta else None
            else:
                image_meta = soup.find("meta", {"property": "og:image"})
                img_url = image_meta.get("content") if image_meta else None
            if img_url:
                current_image_filepath = download_file(img_url, "Images", f"{index_prefix}{sanitized_title} - Art", "jpeg")
                if not current_image_filepath:
                    failed_urls.add(url)
            else:
                record_failure(url, "Image URL not found")
                failed_urls.add(url)

        # If both MP3 and image were downloaded successfully, embed the image into the MP3.
        if options["mp3"] and options["image"] and current_mp3_filepath and current_image_filepath:
            add_image_to_mp3(current_mp3_filepath, current_image_filepath)

        # If no failures for this URL, immediately update the skip file.
        if url not in failed_urls:
            with open(skip_file, "a", encoding="utf-8") as sf:
                sf.write(url + "\n")
            downloaded_set.add(url)
            log_operation(f"✅ Marked URL as processed: {url}")

    if failures:
        with open(failed_file, "a", encoding="utf-8") as f:
            f.write("Final failure details for this run:\n")
            for url, msgs in failures.items():
                f.write(f"URL: {url}\n")
                for msg in msgs:
                    f.write(f"  - {msg}\n")
                f.write("\n")
        log_operation(f"\n❌ Failure details have been appended to {failed_file}")
    else:
        log_operation("\n✅ No failures recorded.")

    retry_failed_urls(failed_urls, options)

if __name__ == "__main__":
    main()

```


```
how does this project get links to suno songs from a playlist and then download all of them?

Directory structure:
└── drummersi-suno-downloader/
    ├── README.md
    ├── LICENSE
    ├── index.html
    ├── package.json
    ├── postcss.config.cjs
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── docs/
    │   ├── index.htm
    │   └── style.css
    ├── public/
    │   └── assets/
    ├── src/
    │   ├── App.css
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── vite-env.d.ts
    │   ├── components/
    │   │   ├── Footer.tsx
    │   │   ├── SectionHeading.tsx
    │   │   └── StatusIcon.tsx
    │   ├── icons/
    │   ├── services/
    │   │   ├── RustFunctions.ts
    │   │   ├── Suno.ts
    │   │   └── Utils.ts
    │   └── styles/
    │       └── notifications.module.css
    └── src-tauri/
        ├── Cargo.lock
        ├── Cargo.toml
        ├── build.rs
        ├── tauri.conf.json
        ├── .gitignore
        ├── capabilities/
        │   └── default.json
        ├── icons/
        │   ├── icon.icns
        │   ├── android/
        │   │   ├── mipmap-hdpi/
        │   │   ├── mipmap-mdpi/
        │   │   ├── mipmap-xhdpi/
        │   │   ├── mipmap-xxhdpi/
        │   │   └── mipmap-xxxhdpi/
        │   └── ios/
        └── src/
            ├── lib.rs
            └── main.rs


Files Content:

================================================
File: README.md
================================================
# Suno Music downloader

A tauri app to easily download entire Suno playlists in a few clicks



================================================
File: LICENSE
================================================
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  1. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  1. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  1. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  1. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  1. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    1.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  1. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  1. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  1. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  1. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  1. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  1. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  1. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  1. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  1. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  1. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  1. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  1. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If the program does terminal interaction, make it output a short
notice like this when it starts in an interactive mode:

    <program>  Copyright (C) <year>  <name of author>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, your program's commands
might be different; for a GUI interface, you would use an "about box".

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU GPL, see
<https://www.gnu.org/licenses/>.

  The GNU General Public License does not permit incorporating your program
into proprietary programs.  If your program is a subroutine library, you
may consider it more useful to permit linking proprietary applications with
the library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.  But first, please read
<https://www.gnu.org/licenses/why-not-lgpl.html>.


================================================
File: index.html
================================================
<!doctype html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Suno Music Downloader</title>
</head>

<body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
</body>

</html>

================================================
File: package.json
================================================
{
  "name": "suno-downloader",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "@mantine/core": "^7.15.3",
    "@mantine/form": "^7.15.3",
    "@mantine/hooks": "^7.15.3",
    "@mantine/modals": "^7.15.3",
    "@mantine/notifications": "^7.15.3",
    "@tabler/icons-react": "^3.28.1",
    "@tauri-apps/api": "^2",
    "@tauri-apps/plugin-clipboard-manager": "^2.2.0",
    "@tauri-apps/plugin-dialog": "~2",
    "@tauri-apps/plugin-fs": "~2",
    "@tauri-apps/plugin-http": "~2",
    "@tauri-apps/plugin-log": "~2",
    "@tauri-apps/plugin-notification": "~2",
    "@tauri-apps/plugin-opener": "^2",
    "@tauri-apps/plugin-process": "~2",
    "filenamify": "^6.0.0",
    "p-limit": "^6.2.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "scroll-into-view-if-needed": "^3.1.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2",
    "@types/react": "^18.3.1",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "postcss": "^8.4.49",
    "postcss-preset-mantine": "^1.17.0",
    "postcss-simple-vars": "^7.0.1",
    "typescript": "~5.6.2",
    "vite": "^6.0.3"
  },
  "packageManager": "yarn@1.22.19+sha1.4ba7fc5c6e704fce2066ecbfb0b0d8976fe62447"
}


================================================
File: postcss.config.cjs
================================================
module.exports = {
    plugins: {
        'postcss-preset-mantine': {},
        'postcss-simple-vars': {
            variables: {
                'mantine-breakpoint-xs': '36em',
                'mantine-breakpoint-sm': '48em',
                'mantine-breakpoint-md': '62em',
                'mantine-breakpoint-lg': '75em',
                'mantine-breakpoint-xl': '88em',
            },
        },
    },
};

================================================
File: tsconfig.json
================================================
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": false,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}


================================================
File: tsconfig.node.json
================================================
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}


================================================
File: vite.config.ts
================================================
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig(async () => ({
    plugins: [react()],

    // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
    //
    // 1. prevent vite from obscuring rust errors
    clearScreen: false,
    // 2. tauri expects a fixed port, fail if that port is not available
    server: {
        port: 1420,
        strictPort: true,
        host: host || false,
        hmr: host
            ? {
                protocol: "ws",
                host,
                port: 1421,
            }
            : undefined,
        watch: {
            // 3. tell vite to ignore watching `src-tauri`
            ignored: ["**/src-tauri/**"],
        },
    },
    css: {
        postcss: './postcss.config.cjs'
    }
}));


================================================
File: docs/index.htm
================================================
<!DOCTYPE html>
<html>

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Suno Music Downloader</title>
    <link rel="stylesheet" href="./style.css" type="text/css" />
    <script type="text/javascript">
        (function (c, l, a, r, i, t, y) {
            c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments) };
            t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
            y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
        })(window, document, "clarity", "script", "pt8ptgfe4u");
    </script>
    <script>
        async function getReleaseAssetUrl(repo, tag = 'latest', assetRegex) {
            const apiUrl = `https://api.github.com/repos/${repo}/releases/${tag}`;

            try {
                const response = await fetch(apiUrl, {
                    headers: {
                        Accept: 'application/vnd.github.v3+json',
                    },
                });

                if (!response.ok) {
                    throw new Error(`GitHub API returned ${response.status}: ${response.statusText}`);
                }

                const release = await response.json();
                const asset = release.assets.find(asset => assetRegex.test(asset.name));

                if (!asset) {
                    throw new Error(`No asset found matching ${assetRegex}`);
                }

                return asset.browser_download_url;
            } catch (error) {
                console.error('Error fetching release asset URL:', error.message);
                return null;
            }
        }


        getReleaseAssetUrl('DrummerSi/suno-downloader', 'latest', /\.msi/)
            .then(url => {
                if (url) {
                    console.log('Download URL:', url);
                    document.getElementById('download-windows').href = url;
                } else {
                    console.log('No matching asset found.');
                }
            });

    </script>
</head>

<body>

    <section class="hero">
        <div class="container">
            <h1>Suno Music Downloader</h1>
            <p>Quickly and easily download your Suno music playlists</p>
            <div class="buttons">
                <a href="https://github.com/DrummerSi/suno-downloader/releases" id="download-windows"
                    class="btn primary">Download for Windows</a>
                <a href="https://github.com/DrummerSi/suno-downloader/" class="btn secondary">View source</a>
            </div>

            <img src="./suno-app.png"
                style="max-width: 100%; margin-top: 20px; filter: drop-shadow(0px 0px 5px #000); " />
        </div>
    </section>

</body>

</html>

================================================
File: docs/style.css
================================================
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #121212; /* Dark background */
  color: #ffffff; /* Light text for contrast */
}

.hero {
  padding: 60px 20px 20px; /* Add padding at the top */
  text-align: center;
  background-color: #121212;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
}

p {
  font-size: 1.2em;
  margin-bottom: 30px;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn {
  text-decoration: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 1em;
  transition: background-color 0.3s;
}

.btn.primary {
  background-color: #1e88e5; /* Primary button color */
  color: #ffffff;
}

.btn.primary:hover {
  background-color: #1565c0; /* Darker shade on hover */
}

.btn.secondary {
  background-color: #ffffff; /* Secondary button color */
  color: #121212;
}

.btn.secondary:hover {
  background-color: #e0e0e0; /* Slightly darker on hover */
}

================================================
File: src/App.css
================================================

html, body, #root {
    height: 100vh;
}


/* .logo.vite:hover {
  filter: drop-shadow(0 0 2em #747bff);
}

.logo.react:hover {
  filter: drop-shadow(0 0 2em #61dafb);
}
:root {
  font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;

  color: #0f0f0f;
  background-color: #f6f6f6;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

.container {
  margin: 0;
  padding-top: 10vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: 0.75s;
}

.logo.tauri:hover {
  filter: drop-shadow(0 0 2em #24c8db);
}

.row {
  display: flex;
  justify-content: center;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}

a:hover {
  color: #535bf2;
}

h1 {
  text-align: center;
}

input,
button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  color: #0f0f0f;
  background-color: #ffffff;
  transition: border-color 0.25s;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
}

button {
  cursor: pointer;
}

button:hover {
  border-color: #396cd8;
}
button:active {
  border-color: #396cd8;
  background-color: #e8e8e8;
}

input,
button {
  outline: none;
}

#greet-input {
  margin-right: 5px;
}

@media (prefers-color-scheme: dark) {
  :root {
    color: #f6f6f6;
    background-color: #2f2f2f;
  }

  a:hover {
    color: #24c8db;
  }

  input,
  button {
    color: #ffffff;
    background-color: #0f0f0f98;
  }
  button:active {
    background-color: #0f0f0f69;
  }
} */


================================================
File: src/App.tsx
================================================
import "./App.css";

import * as path from "@tauri-apps/api/path"

import { ActionIcon, AppShell, Badge, Box, Button, CloseButton, Divider, FileInput, Flex, Group, Image, NavLink, Paper, Popover, Progress, Stack, Table, Text, TextInput, Title } from "@mantine/core"
import { BaseDirectory, create } from "@tauri-apps/plugin-fs";
import { IconBrandGithub, IconCoffee, IconFolder, IconFolderFilled, IconHelp, IconHelpCircle, IconHelpCircleFilled, IconHelpSmall, IconLink, IconSolarElectricity, IconVinyl } from "@tabler/icons-react";
import Suno, { IPlaylist, IPlaylistClip, IPlaylistClipStatus } from "./services/Suno";
import { addImageToMp3, deletePath, ensureDir, writeFile } from "./services/RustFunctions";
import { delay, getRandomBetween, showError, showSuccess } from "./services/Utils";
import { useEffect, useRef, useState } from "react";

import Footer from "./components/Footer";
import SectionHeading from "./components/SectionHeading";
import StatusIcon from "./components/StatusIcon";
import { exit } from '@tauri-apps/plugin-process'
import { fetch } from "@tauri-apps/plugin-http"
import filenamify from "filenamify"
import { invoke } from "@tauri-apps/api/core";
import { modals } from "@mantine/modals";
import { open as openDialog } from "@tauri-apps/plugin-dialog";
import pLimit from "p-limit"
import reactLogo from "./assets/react.svg";
import scrollIntoView from "scroll-into-view-if-needed"
import { sendNotification } from "@tauri-apps/plugin-notification";

function App() {

    const [playlistUrl, setPlaylistUrl] = useState("")
    const [saveFolder, setSaveFolder] = useState("")
    const [isGettingPlaylist, setIsGettingPLaylist] = useState(false)
    const [isDownloading, setIsDownloading] = useState(false)
    const [downloadPercentage, setDownloadPercentage] = useState(0)
    const [completedItems, setCompletedItems] = useState(0)

    const songTable = useRef<HTMLTableElement>(null);

    const [playlistData, setPlaylistData] = useState<IPlaylist | null>(null)
    const [playlistClips, setPlaylistClips] = useState<IPlaylistClip[]>([])

    const [footerView, setFooterView] = useState<1 | 2>(1)

    const getPlaylist = async () => {
        setIsGettingPLaylist(true)
        setPlaylistData(null)
        setPlaylistClips([])
        try {
            const data = await Suno.getSongsFromPlayList(playlistUrl)
            setPlaylistData(data[0])
            setPlaylistClips(data[1])
        } catch (err) {
            console.log(err)
            showError("Failed to fetch playlist data. Make sure you entered a valid link")
        }
        setIsGettingPLaylist(false)
    }

    const selectOutputFolder = async () => {
        const dir = await openDialog({
            title: "Select Output Folder",
            directory: true,
            canCreateDirectories: true
        })
        if (dir) setSaveFolder(dir)
    }

    const updateClipStatus = (id: string, status: IPlaylistClipStatus) => {
        setPlaylistClips((prevClips) =>
            prevClips.map((clip) =>
                clip.id === id ? { ...clip, status: status } : clip
            )
        )
    }

    const scrollToRow = (row: string) => {
        const node = songTable.current?.querySelector(`tr[data-id="row-${row}"]`)
        if (node) scrollIntoView(node, {
            scrollMode: "if-needed",
            behavior: "smooth",
            block: "end"
        })
    }

    const downloadPlaylist = async () => {
        setDownloadPercentage(0)
        setCompletedItems(0)
        setIsDownloading(true)

        //TODO: Proper error checking
        if (!playlistData || !playlistClips) return

        //Create the output directory if it doesn't exist
        const outputDir = await path.join(saveFolder, filenamify(playlistData.name))
        const tmpDir = await path.join(outputDir, "tmp")
        await ensureDir(outputDir)
        await ensureDir(tmpDir)

        //Reset the status of all clips
        setPlaylistClips((prevClips) =>
            prevClips.map((clip) => ({ ...clip, status: IPlaylistClipStatus.None }))
        )

        const limit = pLimit(5)
        const downloadPromises = playlistClips.map((song) => {
            return limit(async () => {
                updateClipStatus(song.id, IPlaylistClipStatus.Processing)

                scrollToRow(song.id)

                // ─── For Testing Only ────────────────────────
                //await delay(getRandomBetween(800, 2000))

                // ─── Live Downloading ────────────────────────
                const response = await fetch(song.audio_url)
                if (response.status !== 200) {
                    console.log("Failed to download song", song.audio_url)
                    updateClipStatus(song.id, IPlaylistClipStatus.Error)
                    return //continue
                }

                const songBuffer = await response.arrayBuffer()
                const songFileName = `${outputDir}\\${song.no.toString().padStart(2, "0")} - ${filenamify(song.title)}.mp3`
                writeFile(songFileName, songBuffer)
                //Try and download and inject the mp3 image
                const response2 = await fetch(song.image_url)
                if (response2.status === 200) {
                    const imageBuffer = await response2.arrayBuffer()
                    const imageFileName = `${tmpDir}\\${filenamify(song.id)}.jpg`
                    writeFile(imageFileName, imageBuffer)
                    addImageToMp3(songFileName, imageFileName)
                }

                // ─── Update The Playlist Data ────────────────
                updateClipStatus(song.id, IPlaylistClipStatus.Success)
                setCompletedItems((completedItems) => completedItems + 1)
                // const newPercentage = Math.ceil((song.no / playlistClips.length) * 100)
                // if (newPercentage > downloadPercentage) setDownloadPercentage(newPercentage)
            })
        })

        await Promise.all(downloadPromises)

        setIsDownloading(false)
        deletePath(tmpDir)

        //openCompleteModal()
        showSuccess("Playlist downloaded successfully")
    }

    const formatSecondsToTime = (seconds: number) => {
        const roundedSeconds = Math.round(seconds)
        const mins = Math.floor(roundedSeconds / 60)
        const secs = roundedSeconds % 60
        return `${mins}:${secs.toString().padStart(2, "0")}`
    }

    useEffect(() => {
        const initSavePath = async () => {
            const defaultSavePath = await path.audioDir()
            setSaveFolder(defaultSavePath)
        }
        initSavePath()
    }, [])

    useEffect(() => {
        //If we're downloading, show the download progress
        if (isDownloading) {
            setFooterView(2)
        } else {
            setFooterView(1)
        }
    }, [isDownloading])


    useEffect(() => {
        const totalItems = playlistClips.length
        const newPercentage = Math.ceil((completedItems / totalItems) * 100)
        setDownloadPercentage(newPercentage)
    }, [completedItems])


    // const updatePercentage = () => {
    //     const totalItems = playlistClips.length
    //     const completedItems = playlistClips.filter((clip) =>
    //         clip.status === IPlaylistClipStatus.Success
    //     ).length

    //     console.log(JSON.stringify(playlistClips.filter((clip) =>
    //         clip.status === IPlaylistClipStatus.Success
    //     ), null, 4))

    //     const percentage = Math.ceil((completedItems / totalItems) * 100)
    //     console.log(playlistClips, totalItems, completedItems, percentage)
    //     setDownloadPercentage(percentage)
    // }

    const openCompleteModal = () => modals.open({
        title: 'Operation complete',
        centered: true,
        withCloseButton: false,
        children: (
            <Stack gap={20}>
                <Text>Your playlist has been downloaded successfully</Text>
                <Flex justify="flex-end">
                    <Button onClick={() => modals.closeAll()}>Close</Button>
                </Flex>
            </Stack>
        )
    });

    return (
        <AppShell
            header={{ height: 50 }}
            padding="lg"
        >
            <AppShell.Header>
                <Box h="100%" data-tauri-drag-region>
                    <Flex justify="space-between" h="100%" w="100%" data-tauri-drag-region>
                        <Flex
                            h="100%"
                            w="100%"
                            justify="flex-start"
                            align="center"
                            style={{
                                userSelect: "none",
                            }}
                            data-tauri-drag-region>
                            <Group gap={6} ml={10}>
                                <IconVinyl />
                                <Text>Suno Music Downloader</Text>
                            </Group>
                        </Flex>
                        <CloseButton onClick={() => exit(1)} />
                    </Flex>
                </Box>
            </AppShell.Header>
            <AppShell.Main
                style={{
                    display: "flex",
                    flexDirection: "column", // Stacks children vertically
                    height: "100vh", // Full height of the viewport
                    overflow: "hidden", // Prevent overall layout overflow
                }}
            >
                {/* Top Section */}
                <SectionHeading number="1" title="Paste playlist link">
                    <Popover position="bottom-start" withArrow shadow="lg">
                        <Popover.Target>
                            <ActionIcon variant="subtle" size="sm" color="gray"><IconHelpCircle /></ActionIcon>
                        </Popover.Target>
                        <Popover.Dropdown>
                            <Group w={240} gap={4}>
                                <Image radius="md" src="./assets/copy-playlist.png" />
                                <Text>Navigate to your Suno playlist, and click the 'Copy playlist' button as shown</Text>
                            </Group>
                        </Popover.Dropdown>
                    </Popover>
                </SectionHeading>
                <Flex gap="sm" direction="row" mb={20}>
                    <TextInput
                        flex={1}
                        value={playlistUrl}
                        onChange={(event) => setPlaylistUrl(event.currentTarget.value)}
                        rightSection={<IconLink />}
                        disabled={isGettingPlaylist || isDownloading}
                    />
                    <Button
                        variant="filled"
                        loading={isGettingPlaylist}
                        onClick={getPlaylist}
                        disabled={isGettingPlaylist || isDownloading}
                    >
                        Get playlist songs
                    </Button>
                </Flex>

                {/* Central Section */}
                <SectionHeading number="2" title="Review songs" />
                <Flex
                    bg="dark.8"
                    mb={20}
                    style={{
                        flex: 1, // This grows to occupy remaining space
                        overflowY: "auto", // Scrollable if content exceeds
                        padding: "1rem", // Optional padding
                        borderRadius: "0.5rem",
                        flexFlow: "column"
                    }}
                >
                    <Table verticalSpacing="sm" ref={songTable}>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Img</Table.Th>
                                <Table.Th>Title</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>Length</Table.Th>
                                <Table.Th></Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {playlistData && playlistClips?.map((clip) => (
                                <Table.Tr key={clip.id} data-id={`row-${clip.id}`}>
                                    <Table.Td w={50}>
                                        <Image radius="sm" w={40} fit="contain" src={clip.image_url} />
                                    </Table.Td>
                                    <Table.Td>
                                        <Stack gap={0}>
                                            <Group gap={0}>
                                                <Text
                                                    fw={800} size="md"
                                                // variant="gradient"
                                                // gradient={{ from: "grape", to: "teal", deg: 45 }}
                                                >
                                                    {clip.title}
                                                </Text>
                                                <Badge size="xs"
                                                    variant="gradient"

                                                    gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
                                                    ml={6}
                                                >{clip.model_version}</Badge>
                                            </Group>
                                            <Text size="sm" c="dimmed" lineClamp={1}>{clip.tags}</Text>
                                        </Stack>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right" }}>
                                        <Text ff="monospace">
                                            {formatSecondsToTime(clip.duration)}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "center" }}>
                                        <StatusIcon status={clip.status} />
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                </Flex>

                {/* Bottom Section */}
                <SectionHeading number="3" title="Select folder and download">
                    <Popover position="bottom-start" withArrow shadow="lg">
                        <Popover.Target>
                            <ActionIcon variant="subtle" size="sm" color="gray"><IconHelpCircle /></ActionIcon>
                        </Popover.Target>
                        <Popover.Dropdown w={240}>
                            <Text>
                                In the selected directory, a new folder will be created with the playlist name. This folder will contain the downloaded songs.
                            </Text>
                        </Popover.Dropdown>
                    </Popover>
                </SectionHeading>
                <Flex gap="sm" direction="row" mb={20}>

                    <TextInput
                        flex={1}
                        value={saveFolder}
                        disabled={isDownloading}
                        readOnly
                        onClick={selectOutputFolder}
                        leftSection={<IconFolderFilled />}
                        style={{
                            pointer: "cursor",
                        }}
                    />
                    <Button
                        variant="filled"
                        disabled={isGettingPlaylist || isDownloading || (!playlistData)}
                        loading={isDownloading}
                        onClick={downloadPlaylist}
                    >
                        Download songs
                    </Button>
                </Flex>

                <Footer
                    firstComponent={
                        <Group gap={6}>
                            <Button leftSection={<IconBrandGithub />} variant="subtle" size="xs" component="a" href="http://www.github.com" target="_blank">Open source</Button>
                            <Divider orientation="vertical" />
                            <Button leftSection={<IconCoffee />} variant="subtle" size="xs" component="a" href="https://ko-fi.com/drummer_si" target="_blank">Buy me a coffee</Button>
                        </Group>
                    }
                    secondComponent={
                        <Stack
                            w="100%"
                            h={140}
                            gap={4}
                            pb={10}
                            mt={-5}
                        >
                            <Flex>
                                <Text size="xs">{downloadPercentage}%</Text>
                            </Flex>
                            <Progress value={downloadPercentage} animated />
                        </Stack>
                    }
                    currentView={footerView}
                />
            </AppShell.Main>
        </AppShell >
    )
}

// function App2() {
//     const [greetMsg, setGreetMsg] = useState("");
//     const [name, setName] = useState("");

//     async function greet() {
//         // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
//         setGreetMsg(await invoke("greet", { name }));
//     }

//     async function download() {

//         const response = await fetch("https://cdn1.suno.ai/2023b630-359f-4d44-9529-60c3b472c79a.mp3", {
//             method: "GET",
//         });
//         if (response.status !== 200) {
//             throw new Error("Failed to fetch the file.");
//         }

//         const fileData = new Uint8Array(await response.arrayBuffer())
//         await writeFile('test.mp3', fileData, { baseDir: BaseDirectory.Desktop })

//         console.log("SAVED")

//         sendNotification({
//             title: "Song downloaded",
//             body: "Song downloaded successfully",
//         })

//         // const file = await create('test.mp3', { baseDir: BaseDirectory.Desktop })
//         // await file.write(response.arrayBuffer)
//         // await file.close()
//         // console.log(response)


//         // const response = await fetch("https://cdn1.suno.ai/2023b630-359f-4d44-9529-60c3b472c79a.mp3", {
//         //     method: "GET",
//         //     //responseType: "ArrayBuffer", // Use ArrayBuffer for binary files
//         // });

//         // if (!response.data) {
//         //     throw new Error("Failed to fetch the file.");
//         // }

//         // const savePath = await dialog.save({
//         //     title: "Save File As",
//         //     defaultPath: "downloaded_file", // Default filename
//         // });

//         // if (!savePath) {
//         //     console.log("Save operation cancelled.");
//         //     return;
//         // }

//         // Step 3: Write the file to the selected location
//         // const fileData = new Uint8Array(response.data); // Convert ArrayBuffer to Uint8Array
//         // await fs.writeBinaryFile(savePath, fileData);

//         //console.log(`File successfully saved to: ${savePath}`);


//     }

//     return (
//         <main className="container">
//             <h1>Welcome to Tauri + React</h1>

//             <div className="row">
//                 <a href="https://vitejs.dev" target="_blank">
//                     <img src="/vite.svg" className="logo vite" alt="Vite logo" />
//                 </a>
//                 <a href="https://tauri.app" target="_blank">
//                     <img src="/tauri.svg" className="logo tauri" alt="Tauri logo" />
//                 </a>
//                 <a href="https://reactjs.org" target="_blank">
//                     <img src={reactLogo} className="logo react" alt="React logo" />
//                 </a>
//             </div>
//             <p>Click on the Tauri, Vite, and React logos to learn more.</p>

//             <form
//                 className="row"
//                 onSubmit={(e) => {
//                     e.preventDefault();
//                     greet();
//                 }}
//             >
//                 <input
//                     id="greet-input"
//                     onChange={(e) => setName(e.currentTarget.value)}
//                     placeholder="Enter a name..."
//                 />
//                 <button type="submit">Greet</button>

//                 <button onClick={download}>DOWNLOAD</button>
//             </form>
//             <p>{greetMsg}</p>
//         </main>
//     );
// }

export default App;


================================================
File: src/main.tsx
================================================
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css'

import { MantineProvider, createTheme } from '@mantine/core';

import App from "./App";
import { ModalsProvider } from '@mantine/modals'
import { Notifications } from '@mantine/notifications'
import React from "react";
import ReactDOM from "react-dom/client";

const theme = createTheme({
    /** Put your mantine theme override here */
    primaryColor: "blue",
});


ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <MantineProvider theme={theme} forceColorScheme="dark">
            <ModalsProvider>
                <Notifications />
                <App />
            </ModalsProvider>
        </MantineProvider>
    </React.StrictMode>,
);


================================================
File: src/vite-env.d.ts
================================================
/// <reference types="vite/client" />


================================================
File: src/components/Footer.tsx
================================================
import { Box, Button, Divider, Flex, Group, Stack } from "@mantine/core"
import { FC, useEffect, useRef, useState } from "react"
import { IconBrandGithub, IconCoffee } from "@tabler/icons-react"

import { useScrollIntoView } from "@mantine/hooks"

interface Props {
    firstComponent: JSX.Element
    secondComponent: JSX.Element
    currentView: 1 | 2
}
const Footer: FC<Props> = (props) => {

    const { firstComponent, secondComponent, currentView } = props

    // Scroll hook
    const { targetRef: containerRef } = useScrollIntoView<HTMLDivElement>();


    // Handler to toggle scrolling
    // const toggleView = () => {
    //     const container = containerRef.current;
    //     if (!container) return;

    //     if (isFirstVisible) {
    //         container.scrollTo({
    //             top: container.offsetHeight, // Scroll to second div
    //             behavior: 'smooth',
    //         });
    //     } else {
    //         container.scrollTo({
    //             top: 0, // Scroll back to first div
    //             behavior: 'smooth',
    //         });
    //     }

    //     setIsFirstVisible((prev) => !prev);
    // };

    useEffect(() => {
        const container = containerRef.current
        if (!container) return

        const targetScrollTop = currentView === 1 ? 0 : container.offsetHeight
        //console.log("SCROLL TO", targetScrollTop)
        container.scrollTo({
            top: targetScrollTop,
            behavior: "smooth"
        })
    }, [currentView])


    return (
        <Box
            ref={containerRef}
            h={40}
            bg="dark.8"
            style={{
                overflow: "hidden", // Scrollable if content exceeds
                padding: "0.4rem", // Optional padding
                borderRadius: "0.5rem",
                flexFlow: "column"
            }}
        >
            <Stack>
                <Flex
                    //ref={firstDiv.targetRef}
                    justify="center"
                    wrap="nowrap"
                    align="center"
                >
                    {firstComponent}
                </Flex>
                <Flex
                    //ref={secondDiv.targetRef}
                    justify="center"
                    wrap="nowrap"
                    align="center"
                >
                    {secondComponent}
                </Flex>
            </Stack>
        </Box>
    )
}

export default Footer



================================================
File: src/components/SectionHeading.tsx
================================================
import { Badge, Group, Title } from "@mantine/core"

import { FC } from "react"

interface Props {
    number: string
    title: string
    children?: React.ReactNode
}
const SectionHeading: FC<Props> = (props) => {
    const { number, title, children } = props
    return (
        <Group pb={8} gap={8}>
            <Badge
                circle
                size="lg"
                variant="gradient"
                gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
            >{number}</Badge>
            <Title order={4}>{title}</Title>
            {children}
        </Group>
    )
}

export default SectionHeading

================================================
File: src/components/StatusIcon.tsx
================================================
import { IconCheck, IconSquareRoundedCheckFilled, IconSquareRoundedXFilled } from "@tabler/icons-react"
import { Loader, Text } from "@mantine/core"

import { FC } from "react"
import { IPlaylistClipStatus } from "../services/Suno"

interface Props {
    status: IPlaylistClipStatus
}

const StatusIcon: FC<Props> = (props) => {
    const { status } = props
    switch (status) {
        case IPlaylistClipStatus.None:
            return null

        case IPlaylistClipStatus.Processing:
            return <Loader size="xs" />

        case IPlaylistClipStatus.Success:
            return <Text c="green" mt={6}>
                <IconSquareRoundedCheckFilled />
            </Text>

        case IPlaylistClipStatus.Error:
            return <Text c="red" mt={6}>
                <IconSquareRoundedXFilled />
            </Text>

        default:
            return null
    }
}

export default StatusIcon

================================================
File: src/services/RustFunctions.ts
================================================
import { invoke } from "@tauri-apps/api/core"

export async function addImageToMp3(mp3Path: string, imagePath: string): Promise<string> {
    try {
        const result = await invoke<string>("add_image_to_mp3", { mp3Path, imagePath });
        return result; // "Successfully added image to MP3 at ..."
    } catch (error) {
        console.error("Error adding image to MP3:", error);
        throw new Error(error as string);
    }
}

export async function deletePath(targetPath: string) {
    try {
        const result = await invoke<string>("delete_path", { targetPath });
        console.log(result); // "Directories ensured for path: ..."
    } catch (error) {
        console.error("Failed to delete path:", error);
    }
}

export async function ensureDir(dirPath: string) {
    try {
        const result = await invoke<string>("ensure_directory_exists", { dirPath });
        console.log(result); // "Directories ensured for path: ..."
    } catch (error) {
        console.error("Failed to create directories:", error);
    }
}

export async function writeFile(name: string, content: ArrayBuffer) {
    const uint8ArrayContent = new Uint8Array(content);
    try {
        const result = await invoke("write_file", { name, content: uint8ArrayContent });
        console.log(result); // On success, log the success message
    } catch (error) {
        console.error('Error:', error); // On failure, log the error message
    }
}

================================================
File: src/services/Suno.ts
================================================
export enum IPlaylistClipStatus {
    None,
    Processing,
    Success,
    Error
}

export interface IPlaylist {
    name: string
    image: string
    //clips: IPlaylistClip[] | undefined
}

export interface IPlaylistClip {
    id: string
    no: number
    title: string
    duration: number
    tags: string
    model_version: string
    audio_url: string
    video_url: string
    image_url: string
    image_large_url: string
    status: IPlaylistClipStatus
}

class Suno {

    static async getSongsFromPlayList(url: string): Promise<[IPlaylist, IPlaylistClip[]]> {

        //TODO: Check we're in format: https://suno.com/playlist/8ebe794f-d640-46b6-bde8-121622e1a4c2 (https://suno.com/playlist/liked not supported)
        //Scrape URL: https://studio-api.prod.suno.com/api/playlist/8ebe794f-d640-46b6-bde8-121622e1a4c2/?page=1

        // ─── Extract Playlist Id ─────────────────────────────────────
        const regex = /suno\.com\/playlist\/(.*)/
        const match = url.match(regex)
        let playlistId = ""

        if (match && match[1]) {
            playlistId = match[1]
        } else {
            throw new Error("Invalid URL or no playlist ID found")
        }

        // ─── Fetch Playlist Data ─────────────────────────────────────
        let currentPage = 1
        let songNo = 1
        let endOfPlaylist = false

        let playlistName = ""
        let playListImage = ""
        const clips: IPlaylistClip[] = []

        while (!endOfPlaylist) {
            const response = await fetch(`https://studio-api.prod.suno.com/api/playlist/${playlistId}/?page=${currentPage}`)

            if (response.status !== 200) {
                throw new Error("Failed to fetch playlist data")
            }

            const data = await response.json()
            if (data.playlist_clips.length == 0) {
                endOfPlaylist = true
            } else {
                playlistName = data.name
                playListImage = data.image_url

                data.playlist_clips.forEach(({ clip }: any) => {
                    const itemData: IPlaylistClip = {
                        id: clip.id,
                        no: songNo,
                        title: clip.title,
                        duration: clip.metadata.duration,
                        tags: clip.metadata.tags,
                        model_version: clip.major_model_version,
                        audio_url: clip.audio_url,
                        video_url: clip.video_url,
                        image_url: clip.image_url,
                        image_large_url: clip.image_large_url,
                        status: IPlaylistClipStatus.None
                    }
                    clips.push(itemData)
                    songNo++
                })
            }
            currentPage++
        }

        return [
            {
                name: playlistName,
                image: playListImage
            },
            clips
        ]
    }



}


export default Suno

================================================
File: src/services/Utils.ts
================================================
import classes from "../styles/notifications.module.css";
import { notifications } from "@mantine/notifications";

export const stringToArrayBuffer = (str: string) => {
    // Convert the string to a Uint8Array
    const encoder = new TextEncoder();
    const uint8Array = encoder.encode(str);

    // Return the underlying ArrayBuffer
    return uint8Array.buffer;
}

export const delay = (ms: number): Promise<void> => {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

export const showError = (message: string, title?: string) => {
    notifications.show({
        color: "red",
        title: title || "An error occured",
        message: message,
        position: "bottom-center",
        classNames: classes
    })
}

export const showSuccess = (message: string, title?: string) => {
    notifications.show({
        color: "green",
        title: title || "Success",
        message: message,
        position: "bottom-center",
        classNames: classes
    })
}

export const getRandomBetween = (min: number, max: number) => {
    return Math.random() * (max - min) + min
}

================================================
File: src/styles/notifications.module.css
================================================
.root {
  background-color: var(--notification-color, var(--mantine-primary-color-filled));

  &::before {
    background-color: var(--mantine-color-white);
  }
}

.description,
.title {
  color: var(--mantine-color-white);
}

.closeButton {
  color: var(--mantine-color-white);

  @mixin hover {
    background-color: rgba(0, 0, 0, 0.1);
  }
}

================================================
File: src-tauri/Cargo.toml
================================================
[package]
name = "suno-downloader"
version = "0.1.0"
description = "A Tauri App"
authors = ["you"]
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[lib]
# The `_lib` suffix may seem redundant but it is necessary
# to make the lib name unique and wouldn't conflict with the bin name.
# This seems to be only an issue on Windows, see https://github.com/rust-lang/cargo/issues/8519
name = "suno_downloader_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-opener = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tauri-plugin-dialog = "2"
tauri-plugin-http = "2"
tauri-plugin-fs = "2"
tauri-plugin-clipboard-manager = "2.2.0"
tauri-plugin-notification = "2"
tauri-plugin-log = "2"
id3 = "0.4"
tauri-plugin-process = "2"


================================================
File: src-tauri/build.rs
================================================
fn main() {
    tauri_build::build()
}


================================================
File: src-tauri/tauri.conf.json
================================================
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "Suno Music Downloader",
  "version": "1.0.0",
  "identifier": "com.suno-downloader.app",
  "build": {
    "beforeDevCommand": "yarn dev",
    "devUrl": "http://localhost:1420",
    "beforeBuildCommand": "yarn build",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "Suno Music Downloader",
        "decorations": false,
        "resizable": true,
        "width": 800,
        "height": 900,
        "minWidth": 800,
        "minHeight": 600
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}


================================================
File: src-tauri/.gitignore
================================================
# Generated by Cargo
# will have compiled files and executables
/target/

# Generated by Tauri
# will have schema files for capabilities auto-completion
/gen/schemas


================================================
File: src-tauri/capabilities/default.json
================================================
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Capability for the main window",
  "windows": [
    "main"
  ],
  "permissions": [
    "core:default",
    "core:window:default",
    "core:window:allow-start-dragging",
    "opener:default",
    "dialog:default",
    {
      "identifier": "http:default",
      "allow": [
        {
          "url": "https://*.suno.ai"
        }
      ]
    },
    "fs:default",
    {
      "identifier": "fs:write-all",
      "allow": [
        {
          "path": "$DESKTOP"
        },
        {
          "path": "$DESKTOP/**"
        }
      ]
    },
    "clipboard-manager:default",
    "notification:default",
    "log:default",
    "process:default"
  ]
}

================================================
File: src-tauri/src/lib.rs
================================================
// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

use std::fs;
use std::path::Path;

use id3::frame::Content;
use id3::frame::Frame;
use id3::frame::Picture;
use id3::frame::PictureType;
use id3::{Tag, Version};

#[tauri::command]
fn write_file(name: String, content: Vec<u8>) -> Result<String, String> {
    match fs::write(&name, content) {
        Ok(_) => Ok(format!("File written successfully to {}", name)),
        Err(e) => Err(format!("Failed to write file: {}", e)),
    }
}

#[tauri::command]
fn ensure_directory_exists(dir_path: String) -> Result<String, String> {
    let path = Path::new(&dir_path);

    //Attempt to create the directories if they don't exist
    if let Err(e) = fs::create_dir_all(path) {
        return Err(format!("Failed to create directories: {}", e));
    }

    Ok(format!("Directories ensured for path: {}", dir_path))
}

#[tauri::command]
fn delete_path(target_path: String) -> Result<String, String> {
    let path = Path::new(&target_path);

    if !path.exists() {
        return Ok(format!("Path does not exist. Nothing to do"));
    }

    //Attempt to remove file or directory
    if path.is_file() {
        fs::remove_file(path).map_err(|e| format!("Failed to delete file: {}", e))?;
    } else if path.is_dir() {
        fs::remove_dir_all(path).map_err(|e| format!("Failed to delete directory: {}", e))?;
    } else {
        return Err(format!("Unknown path type: {}", target_path));
    }

    return Ok(format!("Successfully deleted: {}", target_path));
}

#[tauri::command]
fn add_image_to_mp3(mp3_path: String, image_path: String) -> Result<String, String> {
    // Load the MP3 file's ID3 tag or create a new one if it doesn't exist
    let mut tag = Tag::read_from_path(&mp3_path).unwrap_or_else(|_| Tag::new());

    // Read the image data
    let image_data =
        fs::read(&image_path).map_err(|e| format!("Failed to read image file: {}", e))?;

    // Create a Picture frame for the image
    let picture = Picture {
        mime_type: "image/jpeg".to_string(), // Or "image/png" depending on your image format
        picture_type: PictureType::CoverFront, // This indicates it's a front cover
        description: String::from("Cover Art"), // Optional description
        data: image_data,                    // The image data
    };

    // Convert Picture to Frame
    let frame = Frame::with_content("APIC", Content::Picture(picture));

    // Add the picture frame to the tag
    tag.add_frame(frame);

    // Write the updated tag back to the MP3 file
    tag.write_to_path(&mp3_path, Version::Id3v24)
        .map_err(|e| format!("Failed to write ID3 tag: {}", e))?;

    Ok(format!("Successfully added image to MP3 at {}", mp3_path))
}

// #[tauri::command]
// fn greet(name: &str) -> String {
//     format!("Hello, {}! You've been greeted from Rust!", name)
// }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_log::Builder::new().build())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            add_image_to_mp3,
            ensure_directory_exists,
            delete_path,
            write_file,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}


================================================
File: src-tauri/src/main.rs
================================================
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    suno_downloader_lib::run()
}

```

---