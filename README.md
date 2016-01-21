# AndCat

AndCat is an Android application written in [Python](https://www.python.org/) that uses the [Kivy](https://www.python.org/) framework. 

You can do two things with AndCat: send TCP streams and receive TCP streams. This mean you can send files between any other device that's running AndCat, [netcat](https://en.wikipedia.org/wiki/Netcat), or any device that can use TCP sockets.

I made this to learn more about Kivy and to scratch a pain I've always had - transfering larger files from my computer to my phone or tablet. You can read more about how this happened on my [blog](http://mattscodecave.com/posts/a-web-developer-builds-a-kivy-app.html).

### Screenshots

![AndCat - File Transfer screen](http://mattscodecave.com/media/thumbs/andcat2_thumb.png)
![AndCat - Send file screen](http://mattscodecave.com/media/thumbs/andcat_thumb.png)

### Building

I'll make a release build of the app available on the Google Play store soon, for now you gotta build it by hand. If something's not working, there's some [good docs](https://kivy.org/docs/guide/packaging-android.html).

```
pip install -r requirements.txt
buildozer android debug
```

##### License
Copyright (C) 2016 sirMackk

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

##### Graphics Credits
Iconka - https://www.iconfinder.com/icons/182515/cat_tied_yarn_icon
