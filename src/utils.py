import numpy as np
import pandas as pd
import geopandas as gpd
import pickle
import matplotlib.pyplot as plt 
import contextily as ctx
from shapely.geometry import LineString

def temp_return():
    print("The util module works")


def turn_node_to_edge_shp(df_shp, origin_col_name, destination_col_name):
    # df_shp index is the node index
    # feel free to change the origin_col, destination_col names
    # origin_col_name = GEOID_home, destination_col_name = GEOID
    index = pd.MultiIndex.from_product([df_shp.index, df_shp.index], names = [origin_col_name, destination_col_name])
    df_edge_shp = pd.DataFrame(index=index).reset_index()
    
    # define edge_list
    edge_list = []
    
    for idx in range(df_edge_shp.shape[0]):
        origin = df_edge_shp.loc[idx, origin_col_name]
        destination = df_edge_shp.loc[idx, destination_col_name]
        edge = LineString([df_shp.loc[origin, 'geometry'].centroid,
                           df_shp.loc[destination, 'geometry'].centroid])
        edge_list.append(edge)
        if idx%10000 == 0: # check the speed
            print(idx)
    
    # attach edge column.
    df_edge_shp['geometry'] = edge_list
    
    # 
    edge_shp = gpd.GeoDataFrame(df_edge_shp, crs = 'epsg:4269')
    return edge_shp


def turn_df_to_adj(df_asymmetric, df_shp):
    ''' turn an asymmetric dataframe (source to target format) to a symmetric adjacency matrix 
        with the targetted 992 * 992 size '''
    index_list = list(df_shp.sort_index().index)
    df_zeros = pd.DataFrame(np.zeros((df_shp.shape[0], df_shp.shape[0])), 
                                index = df_shp.index,
                                columns = df_shp.index)
    df_symmetric = df_zeros.add(df_asymmetric, fill_value = 0.0)
    df_symmetric = df_symmetric.loc[index_list, index_list] # truly symmetric!
    df_symmetric = np.maximum(df_symmetric.values, df_symmetric.values.T)
    df_symmetric = pd.DataFrame(df_symmetric, 
                                index = df_zeros.index,
                                columns = df_zeros.columns)

    # remove the diagnol values
    np.fill_diagonal(df_symmetric.values, 0.0)
    
    return df_symmetric


    
def plot_node_attributes(node_shp, column_name, title_name, fig_name, save_path, xlim = None, ylim = None):
    '''
    plot the attributes for the nodes in a shapefile
    '''
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off') # Use this. Then you can have nice bound box without white areas.
    
    divider = make_axes_locatable(ax) # for legend size
    cax = divider.append_axes("right", size="8%", pad=0.1) # for legend size

    # randominize the camap
    cmap_list = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
    cmap_choice = cmap_list[np.random.choice(np.arange(5))]

    node_shp.plot(facecolor='w', edgecolor='k', ax = ax)
    node_shp.plot(column = column_name, cmap = cmap_choice, legend=True, ax = ax, cax = cax)  
    
    # alternative cmaps: 'summer', 'OrRd'
    ax.set_title(title_name, fontsize=18)
    
    # x and y lim
    if xlim is not None and ylim is not None:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    
    plt.tight_layout()
    plt.show()
    
#     fig.savefig(save_path+fig_name+'.png')
#     plt.close()



# Define a visualization function to show the spatial names.
def plot_node_with_base_map(df_shp, target_column, title_name, alpha, fig_name, save_path, 
                           xlim = None, ylim = None):
    ### 
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    df_shp_3857 = df_shp.to_crs(epsg=3857) # Need 3857 to add an web map base. 
    fig, ax = plt.subplots(figsize=(15, 15))    
    ax.axis('off')
    
#     divider = make_axes_locatable(ax) # for legend size
#     cax = divider.append_axes("right", size="8%", pad=0.1) # for legend size

    # 
    df_shp_3857.plot(facecolor="None", edgecolor='grey', linewidth=0.1, ax = ax)
    df_shp_3857.plot(column = target_column, alpha = alpha, cmap = 'magma', legend=True, ax = ax)
        
#     for x, y, label in zip(df_shp_3857.geometry.centroid.x, df_shp_3857.geometry.centroid.y, df_shp_3857[target_column]):
#         ax.annotate(label, xy=(x, y))#, xytext=(3, 3), textcoords="offset points")

    if xlim is not None and ylim is not None:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    # 
    ax.set_title(title_name, fontsize=18)

    ctx.add_basemap(ax, zoom = 12, source=ctx.providers.OpenStreetMap.Mapnik) # smaller zoom shows larger words. 
      
    plt.tight_layout()
    fig.savefig(save_path+fig_name+'.png')
    plt.show()
    

















































