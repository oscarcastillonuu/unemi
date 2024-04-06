<script>
	export let item = undefined;
	export let getOptionLabel = undefined;

</script>

<style>
  .customItem {
    display: flex;
    align-items: center;
  }

  .customItem_title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .customItem_name {
    display: inline-block;
    font-weight: 700;
    margin-right: 10px;
  }

  .customItem_tagline {
    display: inline-block;
  }

</style>

<div class="customItem">
  <div class="customItem_title">
    <div class="customItem_tagline">{item.display}</div>
  </div>
</div>