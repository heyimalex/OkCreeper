# OkCreeper

Source from the now defunct OkCreeper, basically as it was the day it died. May you rest in peace...

For those unfamiliar, OkCreeper was a webapp that allowed you to browse OkCupid profiles anonymously. It was getting ~2500 daily unique visitors around the time when OkCupid sent me a takedown request. Sad as it was to see all that hard work gone, it got an outpouring of love on r/okcupid and plenty of fain mail once I spread the bad news, and it felt amazing to have created something that people actually enjoyed interacting with. Thanks everyone...

## Tech

OkCreeper is flask on the backend and uses angular on the frontend. This was my first forray into angular so I can't promise the code is great, but it works well enough. Assets are compiled(compass), minified, gzipped, and uploaded to s3 using a couple of internal tools and [s3tup](https://github.com/HeyImAlex/s3tup), my s3 deployment/configuration library, in order to lighten the load on my very stressed m1 small server. Requests are made using the awesome [requests](https://github.com/kennethreitz/requests) library, and data is parsed from the pages using a combination of ghettorigged regexes and beatifulsoup backed by lxml. Beneath flask is uwsgi running behind nginx in emperor mode, and my deployments were one touch using a few personal ansible playbooks.