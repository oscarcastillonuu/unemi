<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eCategoriaServicios = [];

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/secretary/category', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					}
				} else {
					eCategoriaServicios = res.data['eCategoriaServicios'];
				}
			}
		}

		return {
			props: {
				eCategoriaServicios
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	let load = true;
	export let eCategoriaServicios;

	let itemsBreadCrumb = [{ text: 'Secretaría', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});
</script>

<svelte:head>
	<title>Secretaría - Mis servicios</title>
</svelte:head>
<!-- {#if !load} -->
<BreadCrumb title="Secretaría - Mis servicios" items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="container">
	<div class="container bg-primary rounded-3">
		<!-- row -->
		<div class="row mb-5 align-items-center">
			<!-- col -->
			<div class="col-lg-6 col-12 d-none d-lg-block">
				<div class="d-flex justify-content-center ">
					<!-- img -->
					<div class="position-relative">
						<img
							src="/assets/images/background/girl-image.png"
							alt=""
							class="img-fluid mt-n6"
						/>
						<div class="ms-n12 position-absolute bottom-0 start-0 mb-6">
							<img src="/assets/images/svg/trophy.svg" alt="" />
						</div>
						<!-- img -->
						<div class="me-n4 position-absolute top-0 end-0">
							<img src="/assets/images/svg/target.svg" alt="" />
						</div>
					</div>
				</div>
			</div>
			<div class="col-lg-5 col-12">
				<div class="text-white p-5 p-lg-0">
					<!-- text -->
					<h2 class="h1 text-white">Bienvenidos a los servicios de secretaría</h2>
					<!--<p class="mb-0">
						Instructors from around the world teach millions of students on Geeks. We provide the
						tools and skills to teach what you love.
					</p>-->
					<a href="/alu_secretaria/mis_pedidos" class="btn btn-warning rounded-pill btn-sm mt-4" style="background-color: #fe9900 !important;"
						><i class="bi bi-shop"></i> Mis pedidos</a
					>
				</div>
			</div>
		</div>
	</div>
	<div class="row justify-content-center">
		{#each eCategoriaServicios as eCategoria}
			<div class="col-xl-4 col-lg-6 col-md-6 col-12">
				<div class="card mb-4 card-hover">
					<div class="d-flex justify-content-between align-items-center p-4">
						<div class="d-flex">
							<a href="/alu_secretaria/service/{eCategoria.id}">
								<!-- Img -->

								{#if eCategoria.icono}
									{@html eCategoria.icono}
								{:else}
									<!--<img src="./assets/images/path/path-bootstrap.jpg" alt="" class="avatar-md" />-->
									<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-hand-index avatar-md" viewBox="0 0 16 16">
										<path d="M6.75 1a.75.75 0 0 1 .75.75V8a.5.5 0 0 0 1 0V5.467l.086-.004c.317-.012.637-.008.816.027.134.027.294.096.448.182.077.042.15.147.15.314V8a.5.5 0 1 0 1 0V6.435a4.9 4.9 0 0 1 .106-.01c.316-.024.584-.01.708.04.118.046.3.207.486.43.081.096.15.19.2.259V8.5a.5.5 0 0 0 1 0v-1h.342a1 1 0 0 1 .995 1.1l-.271 2.715a2.5 2.5 0 0 1-.317.991l-1.395 2.442a.5.5 0 0 1-.434.252H6.035a.5.5 0 0 1-.416-.223l-1.433-2.15a1.5 1.5 0 0 1-.243-.666l-.345-3.105a.5.5 0 0 1 .399-.546L5 8.11V9a.5.5 0 0 0 1 0V1.75A.75.75 0 0 1 6.75 1zM8.5 4.466V1.75a1.75 1.75 0 1 0-3.5 0v5.34l-1.2.24a1.5 1.5 0 0 0-1.196 1.636l.345 3.106a2.5 2.5 0 0 0 .405 1.11l1.433 2.15A1.5 1.5 0 0 0 6.035 16h6.385a1.5 1.5 0 0 0 1.302-.756l1.395-2.441a3.5 3.5 0 0 0 .444-1.389l.271-2.715a2 2 0 0 0-1.99-2.199h-.581a5.114 5.114 0 0 0-.195-.248c-.191-.229-.51-.568-.88-.716-.364-.146-.846-.132-1.158-.108l-.132.012a1.26 1.26 0 0 0-.56-.642 2.632 2.632 0 0 0-.738-.288c-.31-.062-.739-.058-1.05-.046l-.048.002zm2.094 2.025z"/>
									  </svg>
								{/if}
							</a>
							<div class="ms-3">
								<h4 class="mb-1">
									<a href="/alu_secretaria/service/{eCategoria.id}" class="text-inherit">
										{eCategoria.nombre}
									</a>
								</h4>
								<p class="mb-0 fs-6">
									<span>{eCategoria.nombre}</span>
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>
