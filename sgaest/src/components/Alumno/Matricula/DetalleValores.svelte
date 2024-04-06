<script lang="ts">
	import { onMount } from 'svelte';
	export let aData;
	let eMatricula = {};
	let eMateriaAsignadas = [];
	let valorArancel = 0;
	let valorMatricula = 0;
	let valorPagar = 0;

	onMount(async () => {
		eMatricula = aData.eMatricula;
		eMateriaAsignadas = aData.eMateriaAsignadas;
		valorArancel = aData.valorArancel;
		valorMatricula = aData.valorMatricula;
		valorPagar = aData.valorPagar;
	});
</script>

<div class="row">
	<div class="col-md-8 col-12">
		<span class="fs-6">Estudiante</span>
		<h5 class="mb-3">{eMatricula.estudiante}</h5>
	</div>
	{#if eMatricula.gruposocioeconomico}
		<div class="col-md-4 col-12">
			<span class="fs-6">Nivel Socio Económico</span>
			<h5 class="mb-3">
				<span class="badge" style={eMatricula.style_color}>{eMatricula.gruposocioeconomico}</span>
			</h5>
		</div>
	{/if}
	<div class="col-12">
		<p class="text-primary">{eMatricula.mensaje}</p>
	</div>
</div>

<div class="table-responsive mb-12">
	<table class="table mb-0 text-nowrap table-borderless">
		<thead class="table-light">
			<tr>
				<th scope="col" class="text-center">Materias</th>
				<th scope="col" class="text-center">Fecha Asignación</th>
				<th scope="col" class="text-center">Créditos</th>
				<th scope="col" class="text-center">Valor </th>
				<th scope="col" class="text-center">Total</th>
			</tr>
		</thead>
		<tbody>
			{#if eMateriaAsignadas.length > 0}
				{#each eMateriaAsignadas as eMateriaAsignada}
					<tr class="text-dark">
						<td
							class="fs-6 {eMateriaAsignada.activo
								? ''
								: 'text-muted text-decoration-line-through'}"
						>
							{#if eMateriaAsignada.activo}<i class="me-3 bi bi-star-fill text-warning fs-6" />{/if}

							{eMateriaAsignada.asignatura} (<b>{eMateriaAsignada.nivel}</b>)
							{#if !eMateriaAsignada.activo}
								<br />
								<span class="badge bg-light-danger text-danger"
									>Eliminada ({eMateriaAsignada.fecha_eliminacion})</span
								>
							{/if}
						</td>
						<td
							class="text-center fs-6 {eMateriaAsignada.activo
								? ''
								: 'text-muted text-decoration-line-through'}"
						>
							{eMateriaAsignada.fecha_asignacion}
						</td>
						<td
							class="text-center fs-6 {eMateriaAsignada.activo
								? ''
								: 'text-muted text-decoration-line-through'}">{eMateriaAsignada.creditos}</td
						>
						<td
							class="text-center fs-6 {eMateriaAsignada.activo
								? ''
								: 'text-muted text-decoration-line-through'}">$ {eMateriaAsignada.valor}</td
						>
						<td
							class="text-end fs-6 {eMateriaAsignada.activo
								? ''
								: 'text-muted text-decoration-line-through'}">$ {eMateriaAsignada.total}</td
						>
					</tr>
				{/each}
			{/if}
		</tbody>
		<tfoot>
			{#if valorArancel > 0}
				<tr class="text-dark">
					<td colspan="3" />
					<td colspan="1" class="pb-0 text-end">Valor Arancel:</td>
					<td class="pb-0 text-end">$ {valorArancel}</td>
				</tr>
			{/if}
			<tr class="text-dark">
				<td colspan="3" />
				<td colspan="1" class="py-0 text-end">Valor Matricula:*</td>
				<td class="py-0 text-end">$ {valorMatricula}</td>
			</tr>
			<tr class="text-dark">
				<td colspan="3" />
				<td colspan="1" class="border-top py-1 fw-bold text-end">Valor Pagar</td>
				<td class="border-top py-1 fw-bold text-end">$ {valorPagar}</td>
			</tr>
		</tfoot>
	</table>
</div>
