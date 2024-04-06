<script lang="ts">
	import { loginIn, browserSet, browserGet, apiGET } from '$lib/utils/requestUtils';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { goto } from '$app/navigation';
	import { variables } from '$lib/utils/constants';
	import { fly } from 'svelte/transition';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import componenteConsultaDocumento from './_modal/consultaDocumento.svelte';
	import componenteCronogramaModalidad from './_modal/cronogramaModalidad.svelte';
	import componenteCronogramaCarrera from './_modal/cronogramaCarrera.svelte';
	import componenteCronogramaJornada from './_modal/cronogramaJornada.svelte';
	import type { UserResponse } from '$lib/interfaces/user.interface';
	import type { CustomError } from '$lib/interfaces/error.interface';
	import { changeText } from '$lib/helpers/buttonText';
	import { loading } from '$lib/store/loadingStore';
	import { addToast } from '$lib/store/toastStore';
	import { onMount } from 'svelte';
	import { navigating } from '$app/stores';
	let aCronograma = {};
	let username = '',
		password = '',
		errors: Array<CustomError>;
	let clientNavegador;
	let clientOS;
	let clientScreensize;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let modalTitle = '';
	let modalDetalleContent;
	let modalClose = false;
	let mSize = 'xs';
	let aDataModal;
	let aModalidades = [];
	let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';

	onMount(async () => {
		await clienteInfo(window);
		//await loadCronograma();
	});

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
	const handleLogin = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (browserGet('refreshToken')) {
			localStorage.removeItem('refreshToken');
		}
		const [res, err] = await loginIn(fetch, 'token/login', {
			username: username,
			password: password,
			clientNavegador: clientNavegador,
			clientOS: clientOS,
			clientScreensize: clientScreensize
		});
		const json = decodeToken(res);
		//console.log(json);
		const response: UserResponse = json;
		if (err.length > 0) {
			const noty = { title: err[0].error, type: 'error', icon: 'error' };
			addToast({ type: 'error', header: 'Ocurrio un error', body: err[0].error });
		} else if (response.tokens) {
			browserSet('refreshToken', response.tokens.refresh);
			browserSet('accessToken', response.tokens.access);
			browserSet('dataSession', JSON.stringify(response));
			await goto('/');
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const closeModal = () => {
		mOpenModalGenerico = false;
		aDataModal = {};
	};

	const actionRun = async (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeModal();
		} else if (action === 'openModalidades') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openModalidades(aModalidades);
		} else if (action === 'openCarreras') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openCarreras(detail.aModalidad);
		} else if (action === 'openJornadas') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openJornadas(detail.aModalidad, detail.aCoordinacion, detail.aCarrera);
		}
	};

	const openModalidades = async (_aModalidades) => {
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (_aModalidades.length > 0) {
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaModalidad;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'lg';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
			aDataModal = { aModalidades: _aModalidades };
		}
	};

	const openCarreras = async (aModalidad) => {
		let aCoordinaciones = [];
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (aModalidad) {
			aModalidad['aCoordinaciones'].forEach((aCoordinacion) => {
				aCoordinaciones.push({ ...aCoordinacion });
			});
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaCarrera;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'xl';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
			console.log(aCoordinaciones);
			aDataModal = {
				aModalidad: { ...aModalidad },
				//aModalidades: [...aModalidades],
				aCoordinaciones: [...aCoordinaciones]
			};
		}
	};

	const openJornadas = async (aModalidad, aCoordinacion, aCarrera) => {
		let aJornadas = [];
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (aCarrera) {
			aCarrera['aSecciones'].forEach((aSeccion) => {
				aJornadas.push({ ...aSeccion });
			});
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaJornada;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'lg';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
			//console.log(aCoordinaciones);
			aDataModal = {
				aModalidad: { ...aModalidad },
				aCoordinacion: { ...aCoordinacion },
				aCarrera: { ...aCarrera },
				aJornadas: [...aJornadas]
			};
		}
	};

	const loadCronograma = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		aModalidades = [];
		const [res, errors] = await apiGET(fetch, 'cronograma', {});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				aCronograma = res.data['aCronograma'] ?? undefined;
				if (aCronograma) {
					if (aCronograma) {
						aCronograma['aModalidades'].forEach((aModalidad) => {
							aModalidades.push({ ...aModalidad });
						});
					}
					await openModalidades(aModalidades);
				}
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const openModalRecoveryPassword = () => {
		aDataModal = {};
		modalDetalleContent = componenteConsultaDocumento;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = '';
		mSize = 'xs';
		mClass = 'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	};
	function handleKeydown(event) {
		// prevent that a space is typed
		if (event.code === 'Space') event.preventDefault();
	}

	function handleInput(event) {
		// remove spaces from pasted text
		username = username.replaceAll(' ', '');
		username = username.replaceAll('-', '');
		username = username.replaceAll('_', '');
		username = username.toLowerCase();
	}
</script>

<svelte:head>
	<title>Inicio de sesión | SGAEstudiante</title>
</svelte:head>
<!-- <div class="h-100 d-lg-flex align-items-end auth-side-img">
	<div class="col-sm-10 auth-content w-auto">
	</div>
</div> -->
<div class="h-100 d-lg-flex align-items-start auth-side-img">
	<div class="col-sm-10 ">
		<div class="d-flex align-items-end flex-column bd-highlight my-3">
			<button
				type="button"
				class="btn btn-lg btn-info mb-0 "
				style="background-color: #264763 !important; border-color: #264763 !important;"
				on:click|preventDefault={openModalRecoveryPassword}
			>
				Consultar credenciales <br /> Curso de Nivelación 1s-2024
			</button>
		</div>
		<!--<img src="./logo.svg" alt="" class="img-fluid" />-->
		<!--<div>
			<h1 class="text-white my-4 m-sm-10 d-none d-xl-block d-xxl-block">
				UNIVERSIDAD ESTATAL DE MILAGRO
			</h1>
			<h4 class="text-white font-weight-normal my-4 m-sm-10 d-none d-xl-block d-xxl-block">
				<strong style="color: #ff6900;">Misión:</strong><br />
				La UNEMI forma profesionales competentes con actitud proactiva y valores éticos, <br />
				desarrolla investigación relevante y oferta servicios que demanda el sector externo, <br />
				contribuyendo al desarrollo de la sociedad.
			</h4>
			<h4 class="text-white font-weight-normal my-4 m-sm-10 d-none d-xl-block d-xxl-block">
				<strong style="color: #ff6900;">Visión:</strong><br />
				Ser una universidad de docencia e investigación.
			</h4>
		</div>-->
	</div>
</div>
<div class="auth-side-form">
	<div class="auth-content">
		<div class="text-center">
			<img
				src="https://sga.unemi.edu.ec//static/logos/sgaplus_blue.svg"
				alt=""
				width="50%"
				height="50%"
				class="img-fluid "
			/>
		</div>
		<!-- <h3 class="mb-4 fw-bold text-center">Entrar al SGAEstudiante</h3> -->
		<h2 class="mb-1 text-center" style="color: orange ">Iniciar sesión</h2>
		<p class="text-center" style="font-size: 14px; line-height: 17px; ">
			Ingrese sus datos de forma correcta
		</p>
		<form on:submit|preventDefault={handleLogin}>
			<div class="input-group mb-2">
				<span class="mdi mdi-name" />
				<span class="input-group-text"><i class="fe fe-user" /></span>
				<input
					bind:value={username}
					on:keydown={handleKeydown}
					on:input={handleInput}
					type="text"
					id="username"
					class="form-control"
					name="username"
					placeholder="Ingrese nombre de usuario"
					required
				/>
			</div>
			<div class="input-group mb-3">
				<span class="input-group-text"><i class="fe fe-lock" /></span>
				<input
					bind:value={password}
					type="password"
					id="password"
					class="form-control"
					name="password"
					placeholder="Ingrese su contraseña"
					required
				/>
			</div>
			<!--<div class="form-group  mt-2">
				<div class="form-check">
					<input class="form-check-input" type="checkbox" value="" id="flexCheckChecked" checked />
					<label class="form-check-label" for="flexCheckChecked"> Save credentials </label>
				</div>
			</div>-->
			<div class="d-grid gap-2">
				<button type="submit" class="btn btn-lg btn-warning mb-0">Entrar</button>
			</div>
		</form>
		<div class="my-2 text-center" style="">
			<!--<a
				href="javascript:void(0);"
				on:click={() => loadCronograma()}
				style="color: #f39c12 !important"><b>Consultar cronograma de matriculación</b></a
			>-->
			<p class="my-1">
				¿No recuerdas tus datos?
				<a
					href="javascript:;"
					class="pe-auto"
					style="color: #005580 !important"
					on:click|preventDefault={openModalRecoveryPassword}
					><b>Recuperar datos</b>
				</a>
			</p>
			<div class="d-md-block d-lg-none">
				<div class="d-grid gap-2 ">
					<button
						type="button"
						class="btn btn-lg btn-info mb-0 "
						style="background-color: #264763 !important; border-color: #264763 !important;"
						on:click|preventDefault={openModalRecoveryPassword}
					>
						Consultar credenciales <br /> Curso de Nivelación 1s-2024
					</button>
				</div>
			</div>
			<p class="my-1 fs-6">
				¿Tienes problemas? <a href="mailto:tic@unemi.edu.ec"> Contacta al administrador</a>.
			</p>
		</div>
		<hr class="my-4" />
		<div class="mt-2 text-center">
			<a
				href="https://www.facebook.com/UNEMIEcuador"
				target="_blank"
				class="btn-social btn-social-outline btn-facebook"
			>
				<i class="fe fe-facebook fs-4" />
			</a>
			<a
				href="https://twitter.com/UNEMIEcuador"
				target="_blank"
				class="btn-social btn-social-outline btn-twitter"
			>
				<i class="fe fe-twitter fs-4" />
			</a>
			<a
				href="https://www.instagram.com/UNEMIEcuador/"
				target="_blank"
				class="btn-social btn-social-outline btn-linkedin"
			>
				<i class="fe fe-linkedin" />
			</a>
			<a
				href="https://www.unemi.edu.ec/"
				target="_blank"
				class="btn-social btn-social-outline btn-github"
			>
				<i class="fe fe-chrome" />
			</a>
		</div>
	</div>
</div>

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		mClose={modalClose}
		title={modalTitle}
		aData={aDataModal}
		size={mSize}
		{mClass}
		on:actionRun={actionRun}
	/>
{/if}

<style>
	.auth-wrapper .auth-content:not(.container) {
		width: auto !important;
	}
</style>
