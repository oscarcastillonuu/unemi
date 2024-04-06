//const facebookPageName = import.meta.env ? import.meta.env.VITE_FACEBOOK_PAGE : '';

const website = {
	author: 'UNEMI-TICS',
	ogLanguage: 'es_EC',
	siteLanguage: 'es_EC',
	siteTitle: 'UNEMI - SGA/Estudiante',
	siteShortTitle: 'SGA/Estudiante',
	siteUrl: import.meta.env ? /** @type {string} */ (import.meta.env.VITE_SITE_URL) : '',
	icon: 'static/icon.png',
	backgroundColor: '#ffffff',
	themeColor: '#012e46',
	description: 'Universidad Estatal de Milagro - SGA/Estudiante',
	keywords: 'UNEMI, SGA-Estudiante',
	icons: [
		{
			src: './pwalogo/72x72.png',
			sizes: '72x72',
			type: 'image/png'
		},
		{
			src: './pwalogo/96x96.png',
			sizes: '96x96',
			type: 'image/png'
		},
		{
			src: './pwalogo/128x128.png',
			sizes: '128x128',
			type: 'image/png'
		},
		{
			src: './pwalogo/144x144.png',
			sizes: '144x144',
			type: 'image/png'
		},
		{
			src: './pwalogo/152x152.png',
			sizes: '152x152',
			type: 'image/png'
		},
		{
			src: './pwalogo/192x192.png',
			sizes: '192x192',
			type: 'image/png'
		},
		{
			src: './pwalogo/384x384.png',
			sizes: '384x384',
			type: 'image/png'
		},
		{
			src: './pwalogo/512x512.png',
			sizes: '512x512',
			type: 'image/png'
		}
	],
	splash_screens: [
		{
			src: './pwalogo/640x1136.png',
			media: '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
		}
	],
	webPush: {
		can: true,
		vapid_key: 'BByk6uECEJsxL4xO5rqAghWY1PV_5c9V6JuOHnRo5o9jWQRr-ciEP9uUvtMNgRhcBm0zBNm0Hq_ukRrTm4V5_0k' //VAPID_PUBLIC_KEY
	}
};

export { website as default };
