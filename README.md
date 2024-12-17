# Python-discord-bot

A fun discord bot coded in python. It has multiple features and quirky responses.

<p align="center">
  <img src="https://github.com/Geryes-Doumit/Python-discord-bot/assets/102948870/6bfc32f0-a8cd-4265-a72a-4b266f543eee" width="800"/>
</p>

## Fun commands

`/joke [lang]`:
Answers with a random joke in the specified language.

`/blague`:
Answers with a random joke in french.

`/meme`:
Sends a random meme using [meme-api](https://github.com/D3vd/Meme_Api).

`/monkey`:
Sends a random image of a monkey using [placemonkeys.com](https://www.placemonkeys.com/).

`/roast user [name] (server_specific)`:
Roasts the specified person. If the server_specific argument is set to True, the roast will be chosen randomly from the server roasts, otherwise it will be from all the available roasts.

`/roast list (server_specific)`:
Shows all available roasts. Choose whether or not you only want the server roasts with server_specific.

`/roast add [roast]`:
Adds a roast to the server roasts (server_specific). The roast must contain '@n' to specify where the name of the person to roast goes.

`/roast delete [index]`:
Deletes the server roast associated with the index. Every server roast's index is shown in the `/roast list` command.

`/poulpi (state)`:
Sends a random image of poulpi ! `state` is either 'happy' or 'sad'.

`/heroswap [face] (hero)`:
Swaps the face of the image with the face of the specified hero. If no hero is specified, the bot will choose a random hero.

`/faceswap [source] [target]`:
Puts the source face on the target face. The target image can be a GIF.

`/heart_locket [image] [orientation] (text) (second_image)`:
Uses [makesweet.com](https://makesweet.com/my/heart-locket) to make and send a heart locket gif animation.

<table align="center">
  <tr>
    <td width="50%" align="center">
      <img src="https://github.com/Geryes-Doumit/Python-discord-bot/assets/102948870/cbed0c84-165a-43da-a29b-a3372718c50d" width="400"/>
    </td>
    <td width="50%" align="center">
      <img src="https://github.com/Geryes-Doumit/Python-discord-bot/assets/102948870/f23bf3d8-7af1-42e2-baab-a0f0b3a11eac" width="240"/>
    </td>
  </tr>
</table>
<p align="center">Faceswap examples</p>

## System commands

`/features`:
Shows a list of all the available features (automatic responses).

`/enable` or `/disable [feature]`:
Activates or deactivates a feature.

`/help`:
Shows the list of available commands.

## My class' specific commands

These commands are only available in a personal server.

`/edt [...]`:
Captures and sends a screenshot of our schedule for the week.

<table align="center">
  <tr>
    <td width="50%" align="center">
      <img src="https://github.com/Geryes-Doumit/Python-discord-bot/assets/102948870/49a69735-7e05-4a94-b256-c4e7fad9b06a" width="500"/>
    </td>
    <!-- <td width="50%" align="center">
      <img src="https://github.com/Geryes-Doumit/Python-discord-bot/assets/102948870/a80417a1-a0c2-4f28-8fad-c8cbc880bfb2" width="200"/>
    </td> -->
  </tr>
</table>
<p align="center">What the edt command looks like</p>

## Automatic responses

The bot analyses every message sent in a server and answers specific ones if the automatic response is enabled for the server.

> **Backflip GIFs:** `<br/>`
> When a message contains 'backflip', the bot will respond with a backflip GIF.

> **Di:** `<br/>`
> If a word starts with 'di' or 'dy', the bot will answer with the rest of the word.

> **Cri:** `<br/>`
> If a word starts with 'cri' or 'cry', the bot will answer with the rest of the word in uppercase.

> **Insults:** `<br/>`
> If a message contains a french insult, the bot will answer with a random response.

To activate or deactivate a feature, use the `/enable` or `/disable` commands.

<footer>
<p align="center">
  Have fun with the code! Created with ❤️ by Geryes.
</p>
</footer>
