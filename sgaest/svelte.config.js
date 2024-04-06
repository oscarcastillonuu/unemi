import adapter from '@sveltejs/adapter-node';
import preprocess from 'svelte-preprocess';
import { resolve } from 'path';
//import copy from 'rollup-plugin-copy';
//import css from 'rollup-plugin-css-only';
//import copyFiles from './tools/copy-files';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://github.com/sveltejs/svelte-preprocess
	// for more information about preprocessors
	preprocess: preprocess(),

	kit: {
		adapter: adapter({ out: 'build' }),
		vite: {
			/*ssr: {
				externo: ['@xstate/svelte']
			},*/
			//ssr: false,
			/*ssr: {
				noExternal: Object.keys(pkg.dependencies || {})
			},*/
			resolve: {
				alias: {
					$components: resolve('./src/components'),
					$dist: resolve('./src/dist'),
					//dedupe: ['@fullcalendar/common']
				}
			},
			optimizeDeps: {
				//include: ['fuzzy', '@fullcalendar/common']
				include: ['fuzzy']
			},
			plugins: [
				//css({ output: 'bundle.css' }),
				//copy({
				//	targets: [{ src: 'node_modules/bootstrap/dist/**/*', dest: './static/lib/bootstrap' }, { src: './node_modules/@pdftron/pdfjs-express/public/**/*', dest: './static/lib/pdfjs' }]
				//}),
				//copy({
				//	targets: [{ src: 'node_modules/bootstrap/dist/**/*', dest: './static/lib/bootstrap' },]
				//}),
			]
		}
	},
	
};

export default config;
