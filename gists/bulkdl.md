# How to bulk download your Suno library
Today my dad asked me for a way to download all of his Suno songs. (He really loves writing songs, and now he can give them life easily. What a time to be alive!).
Luckily, I found this [gist](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c) and it works great, but my dad also wanted to get the videos generated, so I modified it a little.
```javascript
copy(
    [...$('[role="grid"]')[Object.keys($('[role="grid"]')).filter(x => x.startsWith('__reactProps'))[0]].children[0].props.values[0][1].collection]
    .reduce((acc, x) => {
        if (x.value.audio_url) acc.push(x.value.audio_url);
        if (x.value.video_url) acc.push(x.value.video_url);
        return acc;
    }, [])
    .join('\n')
)
```
You just open your browser console and paste it.

What this does is copying the links of all the songs currently displayed in your library, you can save them wherever you want and use your download manager of choice.
Personally I used `wget`, it is this simple:
```bash
wget -i urls.txt
```
If you want to just get your `urls.txt`, this version saves it automatically for you (but you will have your links in different files for each page of your library):
```javascript
let links =
    [...$('[role="grid"]')[Object.keys($('[role="grid"]')).filter(x => x.startsWith('__reactProps'))[0]].children[0].props.values[0][1].collection]
    .reduce((acc, x) => {
        if (x.value.audio_url) acc.push(x.value.audio_url);
        if (x.value.video_url) acc.push(x.value.video_url);
        return acc;
    }, [])
    .join('\n');

let blob = new Blob([links], { type: 'text/plain' });

let a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = 'urls.txt';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
```