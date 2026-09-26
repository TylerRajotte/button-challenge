import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
export default defineConfig({
  base:process.env.BASE_PATH || '/',
  build:{rollupOptions:{input:{demo:fileURLToPath(new URL('./index.html',import.meta.url)),transcript:fileURLToPath(new URL('./transcript.html',import.meta.url))}}},
  server:{host:'0.0.0.0',port:5173,strictPort:true},
  preview:{host:'0.0.0.0',port:4173,strictPort:true},
});
