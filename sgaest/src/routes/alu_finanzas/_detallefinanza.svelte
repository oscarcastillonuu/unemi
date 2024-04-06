<script lang="ts">
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import ModalTipo from '$components/Reporte/ModalTipo.svelte';
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { action_print_ireport } from '$lib/helpers/baseHelper';
	import Swal from 'sweetalert2';
	export let aData;
	let eFactura = {};
	let eRubro = {};
	let ePagos = [];
	let eReporte = {};
	let mOpenModalTipo = false;
	let mToggleModalTipo = () => (mOpenModalTipo = !mOpenModalTipo);
	let aDataModalTipo;

	onMount(async () => {
		//console.log(aData);
		if (aData.eRubro) {
			eRubro = aData.eRubro;
			ePagos = aData.ePagos;
			eReporte = aData.eReporte;
		}
	});

	const toggleModalTipoDescargar = async (factura) => {
		eFactura = factura;
		aDataModalTipo = { aTipos: eReporte.arreglotipos };
		mOpenModalTipo = !mOpenModalTipo;
	};

	const actionDownload = async (event) => {
		mOpenModalTipo = false;
		loading.setLoading(true, 'Cargando, espere por favor...');
		let parms = {};
		let res = undefined;
		const typeFormat = `,${event.detail.type}`;
		parms['n'] = eReporte.nombre;
		parms['id'] = eFactura.idm;
		res = await action_print_ireport(typeFormat, parms);
		if (res !== undefined) {
			if (res.data.es_background) {
				const mensaje = {
					//toast: true,
					position: 'top-center',
					type: 'info',
					icon: 'info',
					title: res.message,
					showConfirmButton: true
					//timer: 6000
				};
				Swal.fire(mensaje);
			} else {
				window.open(`${res.data.reportfile}`, '_blank');
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};
</script>

<div class="card border-0" id="invoice">
	<!-- Card body -->
	<div class="card-body">
		<div class="d-flex justify-content-between mb-6">
			<div>
				<h4 class="mb-0">{eRubro.nombre}</h4>
				<small>Código: #{eRubro.idm}</small>
			</div>
		</div>
		<!-- Row -->
		<div class="row">
			<div class="col-md-4 col-12">
				<span class="fs-6">Tipo</span>
				<h5 class="mb-3">{eRubro.tipo ? eRubro.tipo.nombre : ''}</h5>
			</div>
			<div class="col-md-8 col-12">
				<div class="row">
					<div class="col-lg-4 col-md-12 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<div class="p-4">
								<span class="fs-6 text-uppercase fw-semi-bold">Valor</span>
								<h2 class="mt-4 fw-bold mb-1 d-flex align-items-center h1 lh-1">
									$ {converToDecimal(eRubro.valor)}
								</h2>
								<span class="d-flex justify-content-between align-items-center">
									<span>Fecha</span>
									<span class="badge bg-success ms-2">{eRubro.fecha}</span>
								</span>
							</div>
						</div>
					</div>

					<div class="col-lg-4 col-md-12 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<div class="p-4">
								<span class="fs-6 text-uppercase fw-semi-bold">Pagado</span>
								<h2 class="mt-4 fw-bold mb-1 d-flex align-items-center h1 lh-1">
									$ {converToDecimal(eRubro.total_pagado)}
								</h2>
							</div>
						</div>
					</div>
					<div class="col-lg-4 col-md-12 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<div class="p-4">
								<span class="fs-6 text-uppercase fw-semi-bold">Adeudado</span>
								<h2 class="mt-4 fw-bold mb-1 d-flex align-items-center h1 lh-1">
									$ {converToDecimal(eRubro.saldo)}
								</h2>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Table -->
		<div class="table-responsive mb-12">
			<table class="table mb-0 text-nowrap table-borderless">
				<thead class="table-light">
					<tr>
						<th scope="col" class="text-center">Recibió</th>
						<th scope="col" class="text-center">Documento</th>
						<th scope="col" class="text-center">Número</th>
						<th scope="col" class="text-center">Valor</th>
						<th scope="col" class="text-center">Descargar</th>
					</tr>
				</thead>
				<tbody>
					{#if ePagos.length > 0}
						{#each ePagos as ePago}
							<tr class="text-dark">
								<td class="fs-5 align-middle"
									>{#if ePago.sesion}
										{#if ePago.sesion.caja}
											{ePago.sesion.caja.display}
										{/if}
									{/if} <span class="fs-6 text-muted"> ({ePago.fecha})</span>
									<br /><span class="fs-6 text-muted"> {ePago.tipo}</span>
								</td>
								<td class="fs-6 text-center align-middle">
									<span class="badge bg-success"
										>{#if ePago.factura}FACTURA{:else}RECIBO DE CAJA{/if}</span
									>
								</td>
								<td class="fs-6 text-center align-middle">
									{#if ePago.factura}
										{ePago.factura.numerocompleto ? ePago.factura.numerocompleto : ''}
									{/if}
									{#if ePago.recibocaja}
										{ePago.recibocaja.numerocompleto ? ePago.recibocaja.numerocompleto : ''}
									{/if}
								</td>
								<td class="fs-6 text-center align-middle">$ {converToDecimal(ePago.valortotal)}</td>
								<td class="fs-6 text-center align-middle">
									{#if ePago.idpagoepunemi}
										{#if ePago.urlfacturaepunemi}
											<a href={ePago.urlfacturaepunemi} target="_blank"
												><i class="fe fe-download" />
											</a>
										{/if}
									{:else if ePago.factura}
										{#if eReporte}
											<a
												href="javascript:;"
												on:click={() => toggleModalTipoDescargar(ePago.factura)}
												class="fe fe-download"
												download=""
											/>
										{/if}
									{:else if ePago.recibocaja}
										<a href={ePago.recibocaja.pdfarchivo} target="_blank"
											><i class="fe fe-download" />
										</a>
									{/if}
								</td>
							</tr>
						{/each}
					{:else}<tr class="text-dark">
							<td colspan="4">No registra pagos</td>
						</tr>
					{/if}
				</tbody>
				<tfoot>
					<tr class="text-dark">
						<td colspan="2" />
						<td colspan="1" class="border-top py-1 fw-bold" />
						<td class="border-top py-1 fw-bold" />
						<!-- $478.50 -->
					</tr>
				</tfoot>
			</table>
		</div>
		<!-- <p class="border-top mb-0 ">
			Notes: Invoice was created on a computer and is valid without the signature and seal.
		</p> -->
	</div>
</div>
{#if mOpenModalTipo}
	<ModalTipo
		mToggle={mToggleModalTipo}
		mOpen={mOpenModalTipo}
		aData={aDataModalTipo}
		on:actionDownload={actionDownload}
	/>
{/if}
