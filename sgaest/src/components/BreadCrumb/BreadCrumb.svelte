<script lang="ts">
	import { goto } from '$app/navigation';
	export let title = '';
	export let subtitle = '';
	export let items;
	export let back = undefined;
</script>

<div class="row mb-3">
	<div class="col-lg-12 col-md-12 col-12 mb-2">
		<div class="d-md-flex align-items-center justify-content-between m-0 mx-3">
			<nav aria-label="breadcrumb" class="d-none d-sm-none d-md-block">
				<ol class="breadcrumb">
					<li class="breadcrumb-item">
						<a href="/">Inicio</a>
					</li>
					{#each items as item}
						{#if item.href}
							<li class="breadcrumb-item" aria-current="page">
								<a href={item.href}>{item.text}</a>
							</li>
						{:else}
							<li class="breadcrumb-item {item.active ? 'active' : ''}" aria-current="page">
								{item.text}
							</li>
						{/if}
					{/each}
				</ol>
			</nav>
			{#if back != undefined}
				<div class="d-none d-sm-none d-md-block">
					<a href={back.href} class="btn btn-warning rounded-pill btn-sm py-1">{back.text}</a>
				</div>
			{/if}
		</div>
	</div>
	{#if title}
		<div class="col-lg-12 col-md-12 col-12 mb-2">
			<div class="mx-3 px-1" style="border-left: 4px solid #e9ecef;border-left-color: #FE9900; ">
				<h3 class="h3 fw-bold m-0 p-0" style="color: #1c3247;">{title}</h3>
				{#if subtitle}
					<h6 class="m-0 p-0" style="color: #7C7C7C">{subtitle}</h6>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.breadcrumb > .breadcrumb-item > a {
		color: #0d6efd;
	}
</style>
