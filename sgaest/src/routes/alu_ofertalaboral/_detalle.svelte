<script lang="ts">
	import { onMount } from 'svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';

	export let aData;
	let oferta = {};
	let empresa = {};
	let area = {};
	let sexo = {};
	let canton = {};
	let carreras = [];

	onMount(async () => {
		// console.log(aData);
		if (aData.OfertaLaboral) {
			oferta = aData.OfertaLaboral;
			empresa = oferta.empresa;
			area = oferta.area;
			sexo = oferta.sexo;
			canton = oferta.canton;
			carreras = aData.eCarrera;
		}
	});
</script>
{#if oferta && empresa && area }
<table class="table table-bordered">

	<thead>
		<tr>
			<th style="width: 200px">Empresa:</th>
			<td colspan="3"> {empresa.display } </td>
		</tr>
		<tr>
			<th>Fecha Inicio:</th>
			<td> {oferta.inicio} </td>
			<th>Fecha Fin:</th>
			<td> {oferta.fin} </td>
		</tr>
		<tr>
			<th>Cargo:</th>
			<td colspan="3"> {oferta.cargo}</td>
		</tr>
		<tr>
			<th>Área:</th>
			<td colspan="3"> {area.display}</td>
		</tr>
		<tr>
			<th>Requiere Título:</th>
			<td colspan="3">
				{#if oferta.graduado }
				 <span class="badge bg-warning">SI</span>
				 {:else}
				 <span class="badge bg-danger">NO</span>

				{/if}
			</td>
		</tr>
		<tr>
			<th>Perfil:</th>
			<td colspan="3">{oferta.descripcion}</td>
		</tr>
	
		<tr>
			<th>Tiempo de dedicación:</th>
			<td colspan="3">
				{#if oferta.tiempo == 1 }
					TIEMPO COMPLETO
				{:else}
					{#if oferta.tiempo == 2 }
						MEDIO TIEMPO
					{:else}
						TIEMPO PARCIAL
					{/if}
	
				{/if}
			
			
			
			</td>
		</tr>
	
		<tr>
			<th>Rango de salario:</th>
			<td colspan="3">{ oferta.salario }</td>
		</tr>
		<tr>
			<th>Cantón:</th>
			<td colspan="3">{ canton.display }</td>
		</tr>
	
		<tr>
			<th>Dirección del trabajo:</th>
			<td colspan="3">{ oferta.lugar }</td>
		</tr>
		<tr>
			<th>Carreras:</th>
			<td colspan="3">
				{#if carreras.length > 0}
					{#each carreras as carr}
						{carr.display} <br>
					{/each}								
				{/if}
			</td>
		</tr>
		<tr><th>Sexo:</th>
			{#if sexo }
				<td>{ sexo.display}</td>
			{:else}
				<td>INDISTINTO</td>
			{/if}
			<th>Vacantes:</th>
			{#if oferta.plazas }
			<td>{ oferta.plazas}</td>
			{/if}
		</tr>
	
		</thead>
	</table>
	
{/if}
