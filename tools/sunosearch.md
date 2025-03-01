# # **Suno AI Search Parameters**

### **Sourcegraph Search Parameters**

Sourcegraph is a powerful tool for searching code across multiple repositories, with advanced filtering options.

1. **Find Code Related to Suno AI**

   ```
   repo:suno-ai file:*.js OR file:*.py OR file:*.ts OR file:*.sh
   ```

   - Searches for JavaScript, Python, TypeScript, or Shell files in repositories related to Suno AI.

2. **Search for Specific Functions or Keywords**

   ```
   lang:python def generate_song
   ```

   - Finds Python functions named `generate_song`.

3. **Find API Calls Related to Suno AI**

   ```
   lang:typescript "fetch('https://api.suno.com"
   ```

   - Looks for TypeScript code where Suno AI’s API is being queried.

4. **Search for Open-Source Suno AI Repositories**

   ```
   repo:^github\.com/.*suno.*
   ```

   - Finds repositories on GitHub related to Suno AI.

5. **Find AI Music Generation Code in Python**

   ```
   lang:python "def" "music" "AI"
   ```

   - Searches for AI-related music generation functions in Python.

---

### **Grep.app Search Parameters**

Grep.app is another code search tool that focuses on regex-based searches across repositories.

1. **Search for Code Snippets Related to Suno AI**

   ```
   suno ai lang:python
   ```

   - Looks for Python files containing references to Suno AI.

2. **Find API Calls to Suno AI in Any Language**

   ```
   "https://api.suno.com"
   ```

   - Searches for direct API calls to Suno AI.

3. **Locate AI Music Generation Projects**

   ```
   "generate music" OR "AI composition"
   ```

   - Finds repositories containing AI-generated music code.

4. **Find Open-Source Suno AI Projects**

   ```
   repo:github.com/.*suno.*
   ```

   - Searches for GitHub repositories related to Suno AI.

5. **Search for AI-Powered Song Generation Code**

   ```
   "AI music" file:*.py OR file:*.js
   ```

   - Looks for AI music-related code in Python and JavaScript files.

---
