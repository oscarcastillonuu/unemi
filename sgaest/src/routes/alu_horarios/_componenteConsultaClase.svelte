<script lang="ts">
	import { variables } from '$lib/utils/constants';
	import { stateWS, connect as connectWS } from '$lib/store/socket';
	import { addToast } from '$lib/store/toastStore';
	import { apiPOST, browserGet } from '$lib/utils/requestUtils';
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { Spinner } from 'sveltestrap';
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	const DEBUG = import.meta.env.DEV;
	export let aData;
	let eClase = {};
	let can_reload_class = false;
	let clientNavegador;
	let clientOS;
	let clientScreensize;
	let key_room;
	let socket;
	let is_utilize_ws = false;
	let endPoint;
	let interval;
	const dispatch = createEventDispatcher();

	onMount(async () => {
		clienteInfo(window);
		if (aData.eClase) {
			eClase = aData.eClase;
			can_reload_class = aData.can_reload_class;
			key_room = eClase.action_button.key_room;
			//console.log(key_room);

			const ds = browserGet('dataSession');
			if (ds != null || ds != undefined) {
				const dataSession = JSON.parse(ds);
				const ws = dataSession['websocket'];
				if (ws != undefined && ws.id != undefined) {
					is_utilize_ws = true;
					if (DEBUG) {
						endPoint = `${variables.BASE_WS}`;
					} else {
						endPoint = ws.url;
					}
					is_utilize_ws = key_room != '';
				}
			}
			if (is_utilize_ws) {
				const token = browserGet('accessToken');
				// Create a new websocket
				endPoint = `${endPoint}/ws/room/${key_room}?token=${token}&app=sge`;
				socket = new WebSocket(endPoint);
				socket.onopen = function (e) {
					console.log('[open] Conexión establecida clases');
				};
				socket.onmessage = async function (event) {
					console.log(`[message] Datos recibidos del servidor: ${event.data}`);
					const data: Request = JSON.parse(event.data);
					console.log(data);
					if ('type' in data) {
						const type = data['type'];
						if (type == 'puede_entrar_clases') {
							can_reload_class = true;
							await loadIntervalClass();
						}
					}
				};
				socket.onclose = function (event) {
					console.log('[close] Conexión cerrada correctamente clases');
				};
				socket.onerror = function (error) {
					key_room = '';
					console.log(`[error] ${error.message}`);
				};
				await enterClass();
			}

			if (!is_utilize_ws) {
				interval = setInterval(function () {
					loadIntervalClass();
				}, 60000);
			}
		}
	});

	const loadIntervalClass = async () => {
		if (can_reload_class) {
			await enterClass();
		}
	};

	const clienteInfo = async (window) => {
		var unknown = '-';

		// browser
		const nVer = navigator.appVersion;
		const nAgt = navigator.userAgent;
		let browser = navigator.appName;
		let version = '' + parseFloat(navigator.appVersion);
		let majorVersion = parseInt(navigator.appVersion, 10);
		let nameOffset, verOffset, ix;

		// screen
		let screenSize = '';
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
		const mobile = /Mobile|mini|Fennec|Android|iP(ad|od|hone)/.test(nVer);

		// system
		let os = unknown;
		let clientStrings = [
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

		let osVersion = unknown;

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
			osVersion: osVersion
		};
		//console.log(window.jscd);
		clientNavegador = window.jscd.browser + ' ' + window.jscd.browserMajorVersion;
		clientOS = window.jscd.os + ' ' + window.jscd.osVersion;
		clientScreensize = window.jscd.screen;
	};

	/*$: {
		console.log($stateWS);
		let requests = $stateWS.requests;
		requests.forEach((req) => {
			if (req['type'] == 'demo_init') {
				console.log(req['message']);
			}
		});
	}*/

	const enterClass = async () => {
		can_reload_class = false;

		const [res, errors] = await apiPOST(fetch, 'alumno/horario?time=' + new Date().getTime(), {
			action: 'enterClassEstudiante',
			idc: eClase.id,
			navegador: clientNavegador,
			os: clientOS,
			screensize: clientScreensize,
			key: eClase.action_button.key
		});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			dispatch('actionRun', { action: 'closeModal' });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				dispatch('actionRun', { action: 'closeModal' });
				if (!res.module_access) {
					goto('/');
				}
			} else {
				//console.log(res.data);
				if (!res.data.isWait && res.data.mensaje) {
					//console.log(res.data.datos);
					if (res.data.datos && socket) {
						console.log('entro');
						socket.send(
							JSON.stringify({
								message: 'ping',
								type: 'entro_clase',
								datos: res.data.datos
							})
						);
						socket.close();
					}
					dispatch('actionRun', { action: 'closeModal' });
					const msj = {
						title: `NOTIFICACIÓN`,
						//text: response.hora ? `${response.mensaje} <h3>${response.hora}<h3>`: `${response.mensaje}` ,
						html: res.data.mensaje,
						type: res.data.label_color,
						icon: res.data.label_color,
						showCancelButton: false,
						allowOutsideClick: false,
						confirmButtonColor: '#3085d6',
						cancelButtonColor: '#d33',
						confirmButtonText: 'Ir al meet',
						cancelButtonText: 'Cancelar'
					};
					Swal.fire(msj)
						.then((result) => {
							if (result.value) {
								//window.open(`${self.clase.action_button.url}`, '_blank');
								var a = document.createElement('a');
								a.target = '_blank';
								a.href = eClase.action_button.url;
								a.click();
								goto('/');
								//dispatch('actionRun', { action: 'closeModal' });
								//window.open(self.clase.action_button.url, '_blank');
							}
						})
						.catch((error) => {
							addToast({ type: 'error', header: 'Ocurrio un error', body: error.message });
						});
				} else {
					can_reload_class = true;
				}
			}
		}
	};

	onDestroy(() => {
		if (is_utilize_ws) {
			if (socket) {
				socket.close();
			}
		}
		if (interval) {
			console.log('clearInterval');
			clearInterval(interval);
		}
	});
</script>

<div class="col-auto text-center">
	<h5>
		Espere un (1) minutos, el sistema está consultando si {eClase.profesor_sexo_id == 1
			? 'la profesora'
			: 'el profesor'} ha iniciado la clase.
	</h5>
	<h3>{eClase.asignatura}</h3>
	{#if eClase.profesor}
		<h4 style="font-weight: normal !important;">{eClase.profesor}</h4>
	{/if}
	<Spinner color="info" type="border" style="width: 3rem; height: 3rem;" />
</div>
