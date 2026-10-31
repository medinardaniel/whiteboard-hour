# Object storage: lecture video (component 5)

Each numbered line is one step on screen. *(pause)* marks a break of a second or more.

1. `title` Component five: object storage.
2. `SD` Object storage is a cloud service for files. Each file, called an object, is saved under a name, in a container called a bucket. It's cheap, and practically unlimited. *(pause)*
3. `SD2` You rent it, from Amazon S3, Azure Blob Storage or Google Cloud Storage. Your database keeps only each file's name, a short line of text. *(pause)*
4. `S1` Why not send files to your own servers? A print shop customer uploads ten photos for holiday cards, four megabytes each.
5. `S1b` Every byte passes through your API servers, and if you store the photos in the database, it bloats. Multiply by thousands of orders, and both clog. *(pause)*
6. `S2` The fix is a signed URL: a temporary link that lets someone upload or download one file directly. The API signs ten upload links, each valid for, say, fifteen minutes.
7. `S3` The browser sends the photos straight to storage. Not one byte of them touches your servers. *(pause)*
8. `S3b` Then the browser tells the API it's done, and the database saves ten short names.
9. `S3c` Later, a worker fetches the photos by name, and prints the cards. *(pause)*
10. `S4` So what do you use it for? Uploads, like photos and videos.
11. `S4b` Files you generate, like PDF invoices and exports, shared with a signed download link.
12. `S4c` And public files, served to everyone through a CDN. *(pause)*
13. `S5` Now the numbers. Ten photos at four megabytes is forty megabytes per order. A thousand holiday orders is forty gigabytes. *(pause)*
14. `S6` Without object storage, all forty gigabytes flow through your API servers.
15. `S6b` With signed links, the servers handle only links and names, about ten megabytes. Storage takes the forty gigabytes, which is exactly what it's built for. *(pause)*
16. `S7` Here's where it sits: off to the side. The browser uploads to it directly.
17. `S7b` And when files go out, the CDN serves them, with storage as its source. *(pause)*
18. `S8` Two things to know. Keep the bucket private, and hand out signed links that expire. A public bucket leaks every customer's files.
19. `S8b` And files are written whole. You replace a file; you don't edit part of it. *(pause)*
20. `S9` In the interview, say: the browser uploads straight to storage with a signed URL, so photos never pass through our servers.

## Pronunciation

| On screen | Spoken |
|---|---|
| API | A P I |
| S3 | S three |
| CDN | C D N |
| PDF | P D F |
| URL | U R L |
