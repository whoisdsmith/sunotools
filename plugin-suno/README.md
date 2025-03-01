# @elizaos/plugin-suno

A Suno AI music generation plugin for ElizaOS that enables AI-powered music creation and audio manipulation.

OVERVIEW

The Suno plugin integrates Suno AI's powerful music generation capabilities into ElizaOS, providing a seamless way to:

- Generate music from text prompts with fine-tuned parameters
- Create custom music with advanced control over style, tempo, and key
- Extend existing audio tracks

Original Plugin: <https://github.com/gcui-art/suno-api?tab=readme-ov-file>

INSTALLATION

    npm install @elizaos/plugin-suno

QUICK START

1. Register the plugin with ElizaOS:

    import { sunoPlugin } from '@elizaos/plugin-suno';
    import { Eliza } from '@elizaos/core';

    const eliza = new Eliza();
    eliza.registerPlugin(sunoPlugin);

2. Configure the Suno provider with your API credentials:

    import { sunoProvider } from '@elizaos/plugin-suno';

    sunoProvider.configure({
      apiKey: 'your-suno-api-key'
    });

FEATURES

1. Generate Music (suno.generate-music)
   Generate music using a text prompt with basic control parameters. This is ideal for quick music generation when you need less fine-grained control:

   - Simple text-to-music generation
   - Consistent output quality with default parameters
   - Suitable for most common use cases

    await eliza.execute('suno.generate-music', {
      prompt: "An upbeat electronic dance track with energetic beats",
      duration: 30,
      temperature: 1.0,
      topK: 250,
      topP: 0.95,
      classifier_free_guidance: 3.0
    });

2. Custom Music Generation (suno.custom-generate-music)
   Create music with detailed control over generation parameters. Perfect for when you need precise control over the musical output:

   - Fine-grained control over musical style and structure
   - Reference-based generation using existing audio
   - Control over musical attributes:
     - Style: Specify genres like "classical", "electronic", "rock"
     - Tempo: Set exact BPM (beats per minute)
     - Key and Mode: Define musical key (e.g., "C") and mode ("major"/"minor")
   - Advanced parameter tuning for generation quality

    await eliza.execute('suno.custom-generate-music', {
      prompt: "A melodic piano piece with soft strings",
      duration: 30,
      temperature: 0.8,
      topK: 250,
      topP: 0.95,
      classifier_free_guidance: 3.0,
      reference_audio: "path/to/reference.mp3",
      style: "classical",
      bpm: 120,
      key: "C",
      mode: "major"
    });

3. Extend Audio (suno.extend-audio)
   Extend existing audio tracks to create longer compositions. Useful for:

   - Lengthening existing music pieces
   - Creating seamless loops
   - Generating variations of existing tracks

    await eliza.execute('suno.extend-audio', {
      audio_id: "your-audio-id",
      duration: 60
    });

Generation Parameters Explained:

- temperature: Controls randomness in generation (0.0-1.0+)
  - Lower values (0.1-0.5): More conservative, consistent output
  - Higher values (1.0+): More creative, varied output

- classifier_free_guidance: Controls how closely the output follows the prompt (1.0-20.0)
  - Lower values: More creative interpretation
  - Higher values: Stricter adherence to prompt

- topK/topP: Control the diversity of the generation
  - topK: Limits the number of tokens considered
  - topP: Controls the cumulative probability threshold

API REFERENCE

SunoProvider Configuration
The Suno provider accepts the following configuration options:

    interface SunoConfig {
      apiKey: string;
    }

Action Parameters:

1. Generate Music (suno.generate-music)
    interface GenerateParams {
      prompt: string;
      duration?: number;        // Duration in seconds
      temperature?: number;     // Controls randomness
      topK?: number;           // Top K sampling
      topP?: number;           // Top P sampling
      classifier_free_guidance?: number; // Guidance scale
    }

2. Custom Generate Music (suno.custom-generate-music)
    interface CustomGenerateParams {
      prompt: string;
      duration?: number;
      temperature?: number;
      topK?: number;
      topP?: number;
      classifier_free_guidance?: number;
      reference_audio?: string; // Path to reference audio file
      style?: string;          // Musical style
      bpm?: number;            // Beats per minute
      key?: string;            // Musical key
      mode?: string;           // Musical mode (e.g., "major", "minor")
    }

3. Extend Audio (suno.extend-audio)
    interface ExtendParams {
      audio_id: string;        // ID of the audio to extend
      duration: number;        // Additional duration in seconds
    }

Response Type:
    interface GenerationResponse {
      id: string;             // Generated audio ID
      status: string;         // Status of the generation
      url?: string;          // URL to download the generated audio
      error?: string;        // Error message if generation failed
    }

ERROR HANDLING

The plugin includes built-in error handling for common scenarios:

    try {
      await eliza.execute('suno.generate', params);
    } catch (error) {
      if (error.code === 'SUNO_API_ERROR') {
        // Handle API-specific errors
      }
      // Handle other errors
    }

EXAMPLES

Creating a Pop Song:

    const result = await eliza.execute('suno.generate-music', {
      prompt: "Create a pop song with vocals, drums, and guitar",
      duration: 180,
      temperature: 1.0,
      classifier_free_guidance: 3.5
    });

Creating a Custom Classical Piece:

    const result = await eliza.execute('suno.custom-generate-music', {
      prompt: "A classical piano sonata in the style of Mozart",
      duration: 120,
      temperature: 0.8,
      style: "classical",
      bpm: 120,
      key: "C",
      mode: "major"
    });

Extending an Existing Track:

    const extended = await eliza.execute('suno.extend-audio', {
      audio_id: "existing-track-id",
      duration: 60
    });

## Overview

This project is a Suno AI music generation plugin for ElizaOS. It allows users to generate and manipulate music via the Suno AI API. The plugin provides three core functionalities:

1. **`generate-music` (GenerateMusic):**  Generates music based on a text prompt.  Users can specify the `prompt`, `duration`, `temperature`, `topK`, `topP`, and `classifier_free_guidance`. This action provides a simplified interface for music generation, with sensible default values for most parameters.

2. **`custom-generate-music` (CustomGenerateMusic):** Offers more granular control over music generation.  In addition to the parameters available in `generate-music`, users can also specify `reference_audio`, `style`, `bpm`, `key`, and `mode`.  This allows for highly customized music creation.

3. **`extend-audio` (ExtendAudio):**  Extends the duration of an existing audio track.  Users provide the `audio_id` and the desired additional `duration`.

The project is structured as follows:

- **`src/providers/suno.ts`:**  Defines the `SunoProvider` class, which handles communication with the Suno AI API.  It requires a `SUNO_API_KEY` to be configured in the ElizaOS runtime settings. The provider's `request` method handles making API requests, including authentication.

- **`src/actions/generate.ts`:** Implements the `generate-music` action.  It uses the `SunoProvider` to make a request to the `/generate` endpoint.

- **`src/actions/customGenerate.ts`:** Implements the `custom-generate-music` action. It uses the `SunoProvider` to interact with the `/custom-generate` endpoint, allowing for more detailed control over music generation.

- **`src/actions/extend.ts`:** Implements the `extend-audio` action, using the `SunoProvider` to call the `/extend` endpoint.

- **`src/index.ts`:**  Exports the plugin's main entry point, `sunoPlugin`, which registers the actions and the `SunoProvider`.  It also re-exports the provider and actions for direct use.

- **`src/types/index.ts`:** This file (present in the file paths but marked redundant in types being exported in `src/providers/suno.ts`) defines the TypeScript interfaces for the action parameters (`GenerateParams`, `CustomGenerateParams`, `ExtendParams`) and the API response (`GenerationResponse`).

- **`dist/`:** Contains the compiled JavaScript code and type definitions.

- **`package.json`:**  Contains metadata about the plugin, including dependencies, build scripts, and configuration for ElizaOS. The `agentConfig` section specifies that this is an ElizaOS client plugin and defines the `apiKey` parameter.

- **`README.md`:** Provides detailed documentation for the plugin, including installation instructions, usage examples, API reference, and error handling information.

- **`biome.json`**: Configuration for the Biome code formatter and linter.

- **`tsconfig.json`**: Configuration for compiling the Typescript code.

- **`tsup.config.ts`**: Configuration for creating builds with `tsup`.

- **`.gitignore`:** Specifies files and directories to be ignored by Git.

The plugin uses `tsup` for building and `biome` for linting and formatting. It's designed to be easily integrated into an ElizaOS environment, providing users with a powerful and flexible way to generate and manipulate music using Suno AI. The README.md is comprehensive and includes clear examples for each action.
