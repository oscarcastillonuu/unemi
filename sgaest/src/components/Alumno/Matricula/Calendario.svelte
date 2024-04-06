<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { Icon } from 'sveltestrap';
	export let aData;
	let mensaje = '';
	let pmes = 0;
	let panio = 0;
	let mes = {};
	const dispatch = createEventDispatcher();

	onMount(async () => {
		mensaje = aData.mensaje;
	});

	const actionLoadCalendar = () => {
		dispatch('actionRun', {
			action: 'loadCalendar'
		});
	};
</script>

<div class="row">
	<div class="col-md-8 col-12">
		<h5 class="mb-3">{mensaje}</h5>
	</div>
</div>
<div class="table-responsive">
	<table class="table table-sm mb-0 text-nowrap table-border">
		<thead class="table-light">
			<tr>
				<th scope="col" class="text-center" style="width: 5%; vertical-align: middle;"
					><button type="button" class="btn btn-light" on:click={actionLoadCalendar}
						><Icon name="caret-left-fill" /></button
					></th
				>
				<th scope="col" class="text-center" style="width: 90%; vertical-align: middle;" colspan="5"
					>--</th
				>
				<th scope="col" class="text-center" style="width: 5%; vertical-align: middle;"
					><button type="button" class="btn btn-light" on:click={actionLoadCalendar}
						><Icon name="caret-right-fill" /></button
					></th
				>
			</tr>
			<tr>
				<th scope="col" class="text-center" style="vertical-align: middle;">Lunes</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Martes</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Miercoles</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Jueves</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Viernes</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Sábado</th>
				<th scope="col" class="text-center" style="vertical-align: middle;">Domingo</th>
			</tr>
		</thead>
	</table>
</div>
