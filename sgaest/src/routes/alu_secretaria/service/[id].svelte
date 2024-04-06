<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	import { session, page, navigating } from '$app/stores';

	export const load: Load = async ({ params, fetch }) => {
		const id = params.id;
		const ds = browserGet('dataSession');
		let eServicios = [];
		let eServicio = {};
		let eCategoriaServicio = {};
		let cont;
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const [res, errors] = await apiGET(fetch, 'alumno/secretary/service', {
				id: id
			});
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					if (!res.module_access) {
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					console.log(res.data);
					eServicios = res.data.eServicios;
					eCategoriaServicio = res.data.eCategoriaServicio;
					cont = res.data.cont;
					if (eServicios.length > 0) {
						eServicio = eServicios[0];
					}
				}
			}
		} else {
			return {
				status: 302,
				redirect: '/alu_secretaria'
			};
		}

		return {
			props: {
				eServicios,
				eServicio,
				eCategoriaServicio,
				cont,
			}
		};
	};
</script>

<script lang="ts">
	import { apiGET, apiPOST, browserGet, browserSet } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { onMount } from 'svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import { decodeToken } from '$lib/utils/decodetoken';
	import type { UserResponse } from '$lib/interfaces/user.interface';
	import ComponenteProductos from './_productos.svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	export let eServicios;
	export let eServicio;
	export let eCategoriaServicio;
	export let cont;
	let total_pedidos = 0;
	let itemsBreadCrumb = [
		{ text: 'Secretaría', active: false, href: '/alu_secretaria' },
		{ text: `${eCategoriaServicio.nombre}`, active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_secretaria', text: 'Atrás' };
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {});

	const actionRun = (event) => {
		if (event.detail.action === 'totalPedidos'){
			total_pedidos = event.detail.value;
		}
	};
</script>

<svelte:head>
	<title>Secretaría{eCategoriaServicio ? ` - ${eCategoriaServicio.nombre}` : ''}</title>
</svelte:head>
{#if eCategoriaServicio}
	<BreadCrumb title="" items={itemsBreadCrumb} back={backBreadCrumb} />

	<div class="p-4">
		<div class="row">
			<div class="col-lg-12 col-md-12 col-12">
				<!--<div class="mb-8">
					<span class="text-primary mb-3 d-block text-uppercase fw-semi-bold ls-lg">Secretaría</span
					>
					<h2 class="mb-1 display-4 fw-bold">{eCategoriaServicio.nombre}</h2>
					{#if eCategoriaServicio.descripcion}
						<p class="mb-0 lead">
							{eCategoriaServicio.descripcion}
						</p>
					{/if}
				</div>-->
				<div class="pb-4 mb-4 d-lg-flex justify-content-between align-items-center">
					<div class="mb-3 mb-lg-0">
						<h1 class="mb-0 h2 fw-bold">{eCategoriaServicio.nombre}</h1>
						{#if eCategoriaServicio.descripcion}
							<p class="mb-0 lead">
								{eCategoriaServicio.descripcion}
							</p>
						{/if}
					</div>
					<div class="d-flex">
						<a
							href="/alu_secretaria/mis_pedidos"
							class="btn btn-warning rounded-pill position-relative" style="background-color: #fe9900 !important;"
							>
							<span class="position-absolute start-100 translate-middle badge rounded-pill" style="background-color: #4597bf !important;"><!-- {total_pedidos} --> {cont}</span>
							<i class="bi bi-shop"></i> Mis pedidos
						</a>
					</div>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="col-md-12">
				<!-- Nav tab -->
				<ul class="nav nav-lb-tab mb-6" id="service-tab" role="tablist">
					{#each eServicios as _eServicio}
						<li class="nav-item" role="presentation">
							<a
								class="nav-link {eServicio.id === _eServicio.id ? 'active show' : ''}"
								id="service_{_eServicio.id}"
								data-bs-toggle="pill"
								href="#ids_{_eServicio.id}"
								role="tab"
								aria-controls="ids-{_eServicio.id}"
								aria-selected="true"
								>{_eServicio.nombre}								
							</a>
						</li>
					{/each}
				</ul>
				<div class="tab-content" id="service-content">
					{#each eServicios as _eServicio}
						<div
							class="tab-pane fade {eServicio.id === _eServicio.id ? 'active show' : ''}"
							role="tabpanel"
							id="ids_{_eServicio.id}"
							aria-labelledby="ids-{_eServicio.id}"
						>
							<ComponenteProductos eServicio={_eServicio} on:actionRun={actionRun} />
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
{/if}
