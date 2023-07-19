<template>
  <aside class="sidebar-nav-wrapper" style="overflow-x: hidden;">
    <div class="navbar-logo">
      <a href="">
        <img src="@/assets/images/logo_biocad.jpg" alt="logo" style="width: 60%"/>
      </a>
    </div>
    <nav class="sidebar-nav">
      <ul>
         <li class="nav-item">
          <router-link :to="{ name: 'camera' }">
             <span class="icon">
                <svg width="22" height="22" viewBox="0 0 22 22">
                  <path
                      d="M17.4167 4.58333V6.41667H13.75V4.58333H17.4167ZM8.25 4.58333V10.0833H4.58333V4.58333H8.25ZM17.4167 11.9167V17.4167H13.75V11.9167H17.4167ZM8.25 15.5833V17.4167H4.58333V15.5833H8.25ZM19.25 2.75H11.9167V8.25H19.25V2.75ZM10.0833 2.75H2.75V11.9167H10.0833V2.75ZM19.25 10.0833H11.9167V19.25H19.25V10.0833ZM10.0833 13.75H2.75V19.25H10.0833V13.75Z"
                  />
                </svg>
              </span>
            <span class="text">Dashboard</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link :to="{ name: 'table' }">
              <span class="icon">
                <svg
                    width="22"
                    height="22"
                    viewBox="0 0 22 22"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                      d="M17.4166 7.33333C18.9383 7.33333 20.1666 8.56167 20.1666 10.0833V15.5833H16.4999V19.25H5.49992V15.5833H1.83325V10.0833C1.83325 8.56167 3.06159 7.33333 4.58325 7.33333H5.49992V2.75H16.4999V7.33333H17.4166ZM7.33325 4.58333V7.33333H14.6666V4.58333H7.33325ZM14.6666 17.4167V13.75H7.33325V17.4167H14.6666ZM16.4999 13.75H18.3333V10.0833C18.3333 9.57917 17.9208 9.16667 17.4166 9.16667H4.58325C4.07909 9.16667 3.66659 9.57917 3.66659 10.0833V13.75H5.49992V11.9167H16.4999V13.75ZM17.4166 10.5417C17.4166 11.0458 17.0041 11.4583 16.4999 11.4583C15.9958 11.4583 15.5833 11.0458 15.5833 10.5417C15.5833 10.0375 15.9958 9.625 16.4999 9.625C17.0041 9.625 17.4166 10.0375 17.4166 10.5417Z"
                  />
                </svg>
              </span>
            <span class="text">Invoice</span>
          </router-link>
        </li>

      </ul>
    </nav>
  </aside>
  <div class="overlay"></div>
</template>

<script>
export default {
  name: "LayoutSlider"
}
</script>

<style scoped>
::-webkit-scrollbar {
  width: 0;
}
</style>