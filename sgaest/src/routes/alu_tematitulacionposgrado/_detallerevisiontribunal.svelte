<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	export let aData;
</script>

{#each aData.revision.obtener_secciones as seccion}
	<!-- content here -->
	<div>
		<table class="table  table-bordered">
			<thead class="table-light">
				<th style="width: 950px;text-align: left;">{seccion.seccion_informe.seccion.display}</th>
				<th class="text-center">SI</th>
				<th class="text-center">NO</th>
			</thead>
			{#each seccion.obtener_preguntas_revision as pregunta, i}
				<!-- content here -->
				<tbody>
					<tr>
						<td>
							{pregunta.seccion_informe_pregunta.display}
						</td>

						<td class="text-center">
							{#if pregunta.respuesta == 'si'}
								X
							{/if}
						</td>

						<td class="text-center">
							{#if pregunta.respuesta == 'no'}
								X
							{/if}
						</td>
					</tr>
					{#if seccion.obtener_preguntas_revision.length == i + 1}
						<!-- content here -->
						<tr>
							<td colspan="3"><label ><b>Observación</b></label>
								<p>{@html seccion.observacion }</p>
							</td>
						</tr>
					{/if}
				</tbody>
			{/each}
		</table>
		<hr class="my-5" />
	</div>
{:else}
	<!-- empty list -->
	Sin Formato
{/each}

<table class="table  table-bordered">
	<thead class="table-light">
		<th style="width: 550px;text-align: left;">DICTAMEN</th>
		<th style="width: 50px;text-align: left;" />
	</thead>
	<tbody>
		{#each aData.revision.obtener_dictamen as dictamen}
			<tr>
				<td>{dictamen[1]}</td>
				<td>
					{#if dictamen[0] == aData.revision.estado}
						X
					{/if}
				</td>
			</tr>
			<!-- empty list -->
		{/each}

		<!-- content here -->
		<tr>
			<td colspan="3"
				><label for="id_observacion_{aData.revision.id}">Observación</label>
				<textarea
					disabled
					name="observacion_{aData.revision.id}"
					class="form-control"
					id="id_observacion_{aData.revision.id}"
					cols="20"
					rows="5">{aData.revision.observacion}</textarea
				>
			</td>
		</tr>
	</tbody>
</table>
