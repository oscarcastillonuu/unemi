<script type="ts">
	import { browserGet, apiPOST } from '$lib/utils/requestUtils';
	import { afterUpdate, onDestroy, onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { fly } from 'svelte/transition';
	import { addToast } from '$lib/store/toastStore';
	let serverdate = new Date();
	let clientdate = new Date();
	let remotenameaddr = '';
	let server_response = '';

	onMount(async () => {
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];

			const [res, errors] = await apiPOST(fetch, 'alumno/footer', {});
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				/*return {
					status: 302,
					redirect: '/'
				};*/
			} else {
				if (res.isSuccess) {
					serverdate = new Date(res.data['hora']);
					remotenameaddr = res.data['remotenameaddr'];
					server_response = res.data['server_response'];
				}
			}
			const interval = setInterval(showTime, 15000);

			return () => {
				clearInterval(interval);
			};
		}
	});
	let checkTime = function (i) {
		if (i < 10) {
			i = '0' + i;
		}
		return i;
	};
	let showTime = function () {
		var m;
		var today = new Date();
		var timediff = today - clientdate;
		var renderdate = new Date(serverdate.getTime() + timediff);
		var h = renderdate.getHours();
		var mer = ' AM';
		if (h > 12) {
			mer = ' PM';
			h -= 12;
		}
		m = renderdate.getMinutes();
		m = checkTime(m);
		let hr = document.getElementById('clock');
		if (hr != undefined) {
			hr.text = h + ':' + m + mer;
		}
	};
</script>

<div
	class="bg-footer text-center navbar-fixed-button"
	id="nav-footer"
	in:fly={{ y: -100, duration: 500, delay: 500 }}
	out:fly={{ duration: 500 }}
>
	<div class="container-fluid">
		<div class="row align-items-center g-0">
			<!-- Desc -->
			<!--<div class="col-md-6 col-12 text-center text-md-start">
              <span style="font-size: 10px;">Sistema de Gestión Académica, Universidad Estatal de Milagro <br>
                 Todos los derechos reservados © 2022</span>
          </div>
            
          <div class="col-12 col-md-6 d-none d-sm-none d-md-block">
              <nav class="nav nav-footer justify-content-center justify-content-md-end">
                  <a class="nav-link active ps-0" href="https://www.unemi.edu.ec/" target="_blank">UNEMI</a>
                  <a class="nav-link" href="https://pregradovirtual.unemi.edu.ec/" target="_blank">Pregrado</a>
                  <a class="nav-link" href="https://admision.unemi.edu.ec/" target="_blank">Admisión</a>
                  <a class="nav-link" href="https://posgrado.unemi.edu.ec/" target="_blank">Posgrado</a>
              </nav>
          </div>-->
			<div class="col-md-12 col-12 text-center" style="">
				<span class="mt-8"
					><b>Universidad Estatal de Milagro</b> Todos los derechos reservados
				</span>
				<span id="ipcapturada">
					- {#if remotenameaddr != ''} {remotenameaddr}{/if} - S{#if server_response != ''}{server_response}{/if}</span
				>
			</div>
			<div style="text-align: right;float: right; margin-top:-19px">
				<a
					href="javascript:;"
					class="text-black"
					style="font-size: 18px;line-height: 18px;color:#222;!important; font-weight: bold"
					id="clock"
				/> &nbsp;&nbsp;
			</div>
		</div>
	</div>
</div>

<style>
	.footer {
		font-size: 11px;
		background-image: linear-gradient(to bottom, #037529, #008a2e);
		background: #1c3247;
		color: #ececec;
		padding-top: 5px;
		z-index: 0;
		height: auto;
	}
	.navbar-fixed-bottom {
		bottom: 0;
		position: fixed;
		right: 0;
		left: 0;
		z-index: 1030;
		margin-bottom: 0;
		overflow: visible;
	}
	.nav-footer > a {
		color: white !important;
	}
	.nav-footer > a:hover {
		color: #d8ac66 !important;
		font-weight: bold;
	}
	.bg-footer {
		/*--bs-bg-opacity: 1;*/
		/*color: #1c3247;*/
		/*height: 25px;*/
		/*font-size: 10px;*/
		/*font-weight: 500;*/
		/*vertical-align: middle;*/
		/*padding-top: 7px;*/
		/*background-color: #e4edf5 !important*/
		bottom: 0;
		position: fixed;
		right: 0;
		left: 0;
		z-index: 1030;
		margin-bottom: 0;
		overflow: visible;
		/*position: fixed;*/
		--bs-bg-opacity: 1;
		color: rgb(28, 50, 71);
		height: 31px;
		right: 0;
		left: 0;
		/* z-index: 1030; */
		margin-bottom: 0;
		font-size: 13px;
		font-weight: 500;
		vertical-align: middle;
		padding-top: 7px;
		background-color: rgb(228, 237, 245) !important;
		clear: both;
	}
</style>
