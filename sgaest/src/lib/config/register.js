import website from '$lib/config/website';
import { variables } from '$lib/utils/constants';
import { browserGet } from '$lib/utils/requestUtils';
const { webPush } = website;

const vapid_key = webPush.vapid_key;

//const serviceWorkerUrl = `http://127.0.0.1:3000/service-worker.js`; //Url de nuestro serviceWorker.
const serviceWorkerUrl = `service-worker.js`; //Url de nuestro serviceWorker.

const registerServiceWorker = async () => {
    // Registramos el Service Worker
    await navigator.serviceWorker.register(serviceWorkerUrl);
};

const registerSw = async () => {
	//console.log('navigator: ', navigator);
	navigator.serviceWorker.ready.then(registration => {
        initialiseState(registration);
    });
};


const initialiseState = (reg) => {
	//console.log("reg.showNotification:", reg.showNotification);
	if (!reg.showNotification) {
		return;
	}

	if (Notification.permission === 'denied') {
		// Swal.fire('Debe permitir las notificaciones para recibir las actualizaciones.', '','warning');
		Notification.requestPermission().then(function (permission) {
			// If the user accepts, let's create a notification
			if (permission === 'granted') {
				var notification = new Notification('Hi there!');
			}
		});
	}

	// @ts-ignore
	if (!'PushManager' in window) {
		return;
	}
	//console.log("PushManager:", window);
	reg.update();
	//console.log('reg:', reg);
	subscribe(reg);
};

const urlB64ToUint8Array = (base64String) => {
	const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
	const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);
	const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));
	return outputData;
};

const subscribe = async (reg) => {
	//console.log("subscribe - reg:", reg);
	const subscription = await reg.pushManager.getSubscription();
	//console.log("subscribe - subscription:", subscription);
	if (subscription) {
		await sendSubData(subscription);
		return;
	}

	const key = vapid_key;
	const options = {
		userVisibleOnly: true,
		...(key && { applicationServerKey: urlB64ToUint8Array(key) })
	};

	const sub = await reg.pushManager.subscribe(options);
	await sendSubData(sub);
};
const unsubscribe = async (reg) => {
	const subscription = await reg.pushManager.getSubscription();
	if (subscription) {
		await sendSubData(subscription);
		return;
	}

	const key = vapid_key;
	const options = {
		userVisibleOnly: true,
		// if key exists, create applicationServerKey property
		...(key && { applicationServerKey: urlB64ToUint8Array(key) })
	};

	const sub = await reg.pushManager.subscribe(options);
	await sendSubData(sub);
};

const getCoordsPosition = async () => {
    try {
        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(position => {
                resolve(position);
            }, error => {
                reject(error);
            })
        });
        return {
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            speed: position.coords.speed,
        };
    } catch (e) {
        //console.log(e.message); //<-- never gets called
        return null;
    }
};


const clienteinfoSw = async (window) => {
	var unknown = '-';

	//Obtener la latitud y longitud de un usuario
	var eGeolocation = null;

	if (navigator.geolocation) {
		eGeolocation = await getCoordsPosition();
	} else {
		// No support...
		//console.log('Navegador no soporta geolocalización');
	}

	// browser
	var nVer = navigator.appVersion;
	var nAgt = navigator.userAgent;
	var browser = navigator.appName;
	var version = '' + parseFloat(navigator.appVersion);
	var majorVersion = parseInt(navigator.appVersion, 10);
	var nameOffset, verOffset, ix;

	// screen
	var screenSize = '';
	if (screen.width) {
		const width = screen.width ? screen.width : '';
		const height = screen.height ? screen.height : '';
		screenSize += '' + width + ' x ' + height;
	}

	// Opera
	if ((verOffset = nAgt.indexOf('Opera')) != -1) {
		browser = 'Opera';
		version = nAgt.substring(verOffset + 6);
		if ((verOffset = nAgt.indexOf('Version')) != -1) {
			version = nAgt.substring(verOffset + 8);
		}
	}
	// Opera Next
	if ((verOffset = nAgt.indexOf('OPR')) != -1) {
		browser = 'Opera';
		version = nAgt.substring(verOffset + 4);
	}
	// MSIE
	else if ((verOffset = nAgt.indexOf('MSIE')) != -1) {
		browser = 'Microsoft Internet Explorer';
		version = nAgt.substring(verOffset + 5);
	}
	// EDGE
	else if (nAgt.indexOf('Edg/') != -1) {
		browser = 'Microsoft Edge';
		version = nAgt.substring(nAgt.indexOf('Edg/') + 4);
	}
	// Chrome
	else if ((verOffset = nAgt.indexOf('Chrome')) != -1) {
		browser = 'Chrome';
		version = nAgt.substring(verOffset + 7);
	}
	// Safari
	else if ((verOffset = nAgt.indexOf('Safari')) != -1) {
		browser = 'Safari';
		version = nAgt.substring(verOffset + 7);
		if ((verOffset = nAgt.indexOf('Version')) != -1) {
			version = nAgt.substring(verOffset + 8);
		}
	}
	// Firefox
	else if ((verOffset = nAgt.indexOf('Firefox')) != -1) {
		browser = 'Firefox';
		version = nAgt.substring(verOffset + 8);
	}
	// MSIE 11+
	else if (nAgt.indexOf('Trident/') != -1) {
		browser = 'Microsoft Internet Explorer';
		version = nAgt.substring(nAgt.indexOf('rv:') + 3);
	}
	// Other browsers
	else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) < (verOffset = nAgt.lastIndexOf('/'))) {
		browser = nAgt.substring(nameOffset, verOffset);
		version = nAgt.substring(verOffset + 1);
		if (browser.toLowerCase() == browser.toUpperCase()) {
			browser = navigator.appName;
		}
	}
	// trim the version string
	if ((ix = version.indexOf(';')) != -1) version = version.substring(0, ix);
	if ((ix = version.indexOf(' ')) != -1) version = version.substring(0, ix);
	if ((ix = version.indexOf(')')) != -1) version = version.substring(0, ix);

	majorVersion = parseInt('' + version, 10);
	if (isNaN(majorVersion)) {
		version = '' + parseFloat(navigator.appVersion);
		majorVersion = parseInt(navigator.appVersion, 10);
	}

	// mobile version
	var mobile = /Mobile|mini|Fennec|Android|iP(ad|od|hone)/.test(nVer);

	// system
	var os = unknown;
	var clientStrings = [
		{ s: 'Windows 10', r: /(Windows 10.0|Windows NT 10.0)/ },
		{ s: 'Windows 8.1', r: /(Windows 8.1|Windows NT 6.3)/ },
		{ s: 'Windows 8', r: /(Windows 8|Windows NT 6.2)/ },
		{ s: 'Windows 7', r: /(Windows 7|Windows NT 6.1)/ },
		{ s: 'Windows Vista', r: /Windows NT 6.0/ },
		{ s: 'Windows Server 2003', r: /Windows NT 5.2/ },
		{ s: 'Windows XP', r: /(Windows NT 5.1|Windows XP)/ },
		{ s: 'Windows 2000', r: /(Windows NT 5.0|Windows 2000)/ },
		{ s: 'Windows ME', r: /(Win 9x 4.90|Windows ME)/ },
		{ s: 'Windows 98', r: /(Windows 98|Win98)/ },
		{ s: 'Windows 95', r: /(Windows 95|Win95|Windows_95)/ },
		{ s: 'Windows NT 4.0', r: /(Windows NT 4.0|WinNT4.0|WinNT|Windows NT)/ },
		{ s: 'Windows CE', r: /Windows CE/ },
		{ s: 'Windows 3.11', r: /Win16/ },
		{ s: 'Android', r: /Android/ },
		{ s: 'Open BSD', r: /OpenBSD/ },
		{ s: 'Sun OS', r: /SunOS/ },
		{ s: 'Linux', r: /(Linux|X11)/ },
		{ s: 'iOS', r: /(iPhone|iPad|iPod)/ },
		{ s: 'Mac OS X', r: /Mac OS X/ },
		{ s: 'Mac OS', r: /(MacPPC|MacIntel|Mac_PowerPC|Macintosh)/ },
		{ s: 'QNX', r: /QNX/ },
		{ s: 'UNIX', r: /UNIX/ },
		{ s: 'BeOS', r: /BeOS/ },
		{ s: 'OS/2', r: /OS\/2/ },
		{
			s: 'Search Bot',
			r: /(nuhk|Googlebot|Yammybot|Openbot|Slurp|MSNBot|Ask Jeeves\/Teoma|ia_archiver)/
		}
	];
	for (var id in clientStrings) {
		var cs = clientStrings[id];
		if (cs.r.test(nAgt)) {
			os = cs.s;
			break;
		}
	}

	var osVersion = unknown;

	if (/Windows/.test(os)) {
		osVersion = /Windows (.*)/.exec(os)[1];
		os = 'Windows';
	}

	switch (os) {
		case 'Mac OS X':
			osVersion = /Mac OS X (10[\.\_\d]+)/.exec(nAgt)[1];
			break;

		case 'Android':
			osVersion = /Android ([\.\_\d]+)/.exec(nAgt)[1];
			break;

		case 'iOS':
			osVersion = /OS (\d+)_(\d+)_?(\d+)?/.exec(nVer);
			osVersion = osVersion[1] + '.' + osVersion[2] + '.' + (osVersion[3] | 0);
			break;
	}
	window.jscd = {
		screen: screenSize,
		browser: browser,
		browserVersion: version,
		browserMajorVersion: majorVersion,
		mobile: mobile,
		os: os,
		osVersion: osVersion,
		eGeolocation: eGeolocation
	};
};

const sendSubData = async (subscription) => {
	try {
		//console.log("subscription:", subscription);
		/*const browser = navigator.userAgent
			.match(/(firefox|msie|chrome|safari|trident|opera|edge)/gi)[0]
			.toLowerCase();*/
		clienteinfoSw(window);
		//console.log("window:", window);
		var navegador = window.jscd.browser + ' ' + window.jscd.browserMajorVersion;
		var os = window.jscd.os;
		var geolocation = window.jscd.eGeolocation;
		var screen_size = window.jscd.screen;
		const data = {
			status_type: 'subscribe',
			subscription: subscription.toJSON(),
			browser: navegador,
			app: 'SIE',
			screen_size: screen_size,
			os: os,
			geolocation: geolocation
		};
		const headers = {};
		const token = browserGet('accessToken');
		headers['Content-Type'] = 'application/json';
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		const body = JSON.stringify(data);
		const res = await fetch(`${variables.BASE_API_URI}/webpush/save_information_notification`, {
			method: 'POST',
			body,
			headers
		}).catch(function (error) {});
		handleResponse(res);
	} catch (e) {}
};

const handleResponse = (res) => {
	//console.log(res.status);
};

export { registerSw as default };
