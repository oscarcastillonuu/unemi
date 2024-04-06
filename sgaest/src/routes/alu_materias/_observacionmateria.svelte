<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';

	export let aData;
	let obervaciones = '';
	let nombremateria = '';
	onMount(async () => {
		console.log(aData);
		if (aData.observacion) {
			obervaciones = aData.observacion;
			nombremateria = aData.nombremateria;
		}
	});
</script>

<div style="background-color: #efefef;" class="p-4" id="mybuscador">
	<div class="row">
		<div class="col-12 text-center">
			<h3 class="">{nombremateria}</h3>
		</div>
	</div>

	<div class="card h-100">
		<div class="card-body">
			<div class="text-center">
				<div class="d-flex justify-content-between border-bottom py-2 mt-4 fs-6">
					<h4>{@html obervaciones}</h4>
				</div>
			</div>
		</div>
	</div>
</div>
