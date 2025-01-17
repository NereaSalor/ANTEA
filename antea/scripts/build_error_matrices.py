import os
import sys
import argparse
import numpy as np

import antea.mcsim   .fastmc3d as fmc

""" To run this script
 python build_error_matrices.py input_folder output_folder
 where:
- input_folder is the folder containing the npz files
with the information of the coincidences used to build the error matrices.
- output_folder is the folder where the error matrices are stored.
 """

def build_error_matrices(input_folder: str, output_folder:str):
    """
    This function calculates the error matrices for a specific simulation.
    Each matrix represents the error in a coordinate (true - reco) as a function
    of the true coordinate.
    """
    true_r1, true_phi1, true_z1 = [], [], []
    reco_r1, reco_phi1, reco_z1 = [], [], []
    true_r2, true_phi2, true_z2 = [], [], []
    reco_r2, reco_phi2, reco_z2 = [], [], []

    sns_response1, sns_response2    = [], []

    first_sipm1, first_sipm2 = [], []
    first_time1, first_time2 = [], []

    true_t1, true_t2                     = [], []
    max_hit_distance1, max_hit_distance2 = [], []

    event_ids = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.npz'):
            print(filename)
            my_file = input_folder + filename
            d       = np.load(my_file)

            true_r1  .extend(d['a_true_r1'])
            true_phi1.extend(d['a_true_phi1'])
            true_z1  .extend(d['a_true_z1'])

            reco_r1  .extend(d['a_reco_r1'])
            reco_phi1.extend(d['a_reco_phi1'])
            reco_z1  .extend(d['a_reco_z1'])

            true_r2  .extend(d['a_true_r2'])
            true_phi2.extend(d['a_true_phi2'])
            true_z2  .extend(d['a_true_z2'])

            reco_r2  .extend(d['a_reco_r2'])
            reco_phi2.extend(d['a_reco_phi2'])
            reco_z2  .extend(d['a_reco_z2'])

            true_t1.extend(d['a_true_time1'])
            true_t2.extend(d['a_true_time2'])

            sns_response1.extend(d['a_sns_response1'])
            sns_response2.extend(d['a_sns_response2'])

            max_hit_distance1.extend(d['a_max_hit_distance1'])
            max_hit_distance2.extend(d['a_max_hit_distance2'])

            event_ids.extend(d['a_event_ids'])

            first_time1.extend(d[f'a_first_time1'])
            first_time2.extend(d[f'a_first_time2'])

            for i in d['a_first_sipm1']:
                first_sipm1.append(i)
            for i in d['a_first_sipm2']:
                first_sipm2.append(i)


    true_r1   = np.array(true_r1)
    true_phi1 = np.array(true_phi1)
    true_z1   = np.array(true_z1)

    reco_r1   = np.array(reco_r1)
    reco_phi1 = np.array(reco_phi1)
    reco_z1   = np.array(reco_z1)

    true_r2   = np.array(true_r2)
    true_phi2 = np.array(true_phi2)
    true_z2   = np.array(true_z2)

    reco_r2   = np.array(reco_r2)
    reco_phi2 = np.array(reco_phi2)
    reco_z2   = np.array(reco_z2)

    true_t1 = np.array(true_t1)
    true_t2 = np.array(true_t2)

    first_time1 = np.array(first_time1)
    first_time2 = np.array(first_time2)
    first_sipm1 = np.array(first_sipm1)
    first_sipm2 = np.array(first_sipm2)

    sns_response1 = np.array(sns_response1)
    sns_response2 = np.array(sns_response2)

    max_hit_distance1 = np.array(max_hit_distance1)
    max_hit_distance2 = np.array(max_hit_distance2)

    event_ids = np.array(event_ids)

    reco_x1 = reco_r1 * np.cos(reco_phi1)
    reco_y1 = reco_r1 * np.sin(reco_phi1)
    reco_x2 = reco_r2 * np.cos(reco_phi2)
    reco_y2 = reco_r2 * np.sin(reco_phi2)


    ### change by hand phi reconstructed as true=~3.14, reco~=-3.14
    reco_phi1[np.abs(reco_phi1 - true_phi1) > 6.] = -reco_phi1[np.abs(reco_phi1 - true_phi1) > 6.]
    reco_phi2[np.abs(reco_phi2 - true_phi2) > 6.] = -reco_phi2[np.abs(reco_phi2 - true_phi2) > 6.]

    true_r   = np.concatenate((true_r1, true_r2))
    true_phi = np.concatenate((true_phi1, true_phi2))
    true_z   = np.concatenate((true_z1, true_z2))
    true_t   = np.concatenate((true_t1, true_t2))

    max_hit_distance = np.concatenate((max_hit_distance1, max_hit_distance2))

    def diff_and_concatenate(true1, true2, reco1, reco2):
        d1 = true1 - reco1
        d2 = true2 - reco2
        diff_matrix = np.concatenate((d1, d2))
        return diff_matrix

    diff_r_matrix   = diff_and_concatenate(true_r1,   true_r2,   reco_r1,   reco_r2)
    diff_phi_matrix = diff_and_concatenate(true_phi1, true_phi2, reco_phi1, reco_phi2)
    diff_z_matrix   = diff_and_concatenate(true_z1,   true_z2,   reco_z1,   reco_z2)

    ave_speed_in_LXe = 0.210 #* units.mm / units.ps

    ### Positions
    pos_1 = np.array([reco_x1, reco_y1, reco_z1]).transpose()
    pos_2 = np.array([reco_x2, reco_y2, reco_z2]).transpose()

    ### Distance of the interaction point from the SiPM seeing the first photon
    dist1 = np.linalg.norm(np.subtract(pos_1, first_sipm1), axis=1)
    dist2 = np.linalg.norm(np.subtract(pos_2, first_sipm2), axis=1)

    reco_t1   = first_time1 - dist1/ave_speed_in_LXe
    reco_t2   = first_time2 - dist2/ave_speed_in_LXe

    diff_reco_t_matrix = (diff_and_concatenate(true_t1, true_t2,     reco_t1,     reco_t2)).flatten()


    d1 = 1 #mm Phot like events
    sel_phot_like  = max_hit_distance <= d1
    sel_compt_like = max_hit_distance > d1

    print(f'Number of interactions for phot = {len(true_t[sel_phot_like])}')


    def get_bins(coord_range, err_range_phot, err_range_compt, coord_width, err_width_phot, err_width_compt):
        coord_bins     = int((coord_range    [1] - coord_range    [0])/coord_width)
        err_bins_phot  = int((err_range_phot [1] - err_range_phot [0])/err_width_phot)
        err_bins_compt = int((err_range_compt[1] - err_range_compt[0])/err_width_compt)
        return coord_bins, err_bins_phot, err_bins_compt


    precision = .3 # mm
    r_max     = 409.7

    r_range           = (380, r_max)
    r_err_range_phot  = (-5, 10)
    r_err_range_compt = (-30, 30)
    r_width           = precision
    r_err_width_phot  = precision
    r_err_width_compt = precision
    r_bins, r_err_bins_phot, r_err_bins_compt = get_bins(r_range,
                                                        r_err_range_phot,
                                                        r_err_range_compt,
                                                        r_width,
                                                        r_err_width_phot,
                                                        r_err_width_compt)

    phi_range           = (-3.15, 3.15)
    phi_err_range_phot  = (-0.01, 0.01)
    phi_err_range_compt = (-0.15, 0.15)
    phi_width           = precision/r_max
    phi_err_width_phot  = precision/r_max
    phi_err_width_compt = precision/r_max
    phi_bins, phi_err_bins_phot, phi_err_bins_compt = get_bins(phi_range,
                                                               phi_err_range_phot,
                                                               phi_err_range_compt,
                                                               phi_width,
                                                               phi_err_width_phot,
                                                               phi_err_width_compt)

    z_range           = (-975, 975)
    z_err_range_phot  = (-3, 3)
    z_err_range_compt = (-100, 100)
    z_width           = precision
    z_err_width_phot  = precision
    z_err_width_compt = precision
    z_bins, z_err_bins_phot, z_err_bins_compt = get_bins(z_range,
                                                         z_err_range_phot,
                                                         z_err_range_compt,
                                                         z_width,
                                                         z_err_width_phot,
                                                         z_err_width_compt)

    t_precision       = 5 # ps
    t_range           = (1000, 3500)
    t_err_range_phot  = (-400, 50)
    t_err_range_compt = (-480, 300)
    t_width           = t_precision
    t_err_width_phot  = t_precision
    t_err_width_compt = t_precision
    t_bins, t_err_bins_phot, t_err_bins_compt = get_bins(t_range,
                                                     t_err_range_phot,
                                                     t_err_range_compt,
                                                     t_width,
                                                     t_err_width_phot,
                                                     t_err_width_compt)


    ### R
    print('')
    print('**** R ****')
    print(f'Number of bins: true r = {r_bins}, err phot = {r_err_bins_phot}, err compt = {r_err_bins_compt}')
    print('')

    ## photoelectric-like events
    print('Phot-like')
    file_name = output_folder + f'errmat_r_phot_like.npz'
    h, eff, xmin, ymin, dx, dy = fmc.compute_error_mat_2d(true_r       [sel_phot_like],
                                                          diff_r_matrix[sel_phot_like],
                                                          bins   = (r_bins,  r_err_bins_phot),
                                                          ranges = (r_range, r_err_range_phot))

    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, dx=dx, dy=dy)
    a = np.sum(h, axis=1)
    print(a.shape, np.count_nonzero(a))

    ## compton-like events
    print('Compt-like')
    file_name = output_folder + f'errmat_r_compt_like.npz'
    h, eff, xmin, ymin, dx, dy = fmc.compute_error_mat_2d(true_r       [sel_compt_like],
                                                          diff_r_matrix[sel_compt_like],
                                                          bins   = (r_bins,  r_err_bins_compt),
                                                          ranges = (r_range, r_err_range_compt))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, dx=dx, dy=dy)
    a = np.sum(h, axis=1)
    print(a.shape, np.count_nonzero(a))


    ### Phi
    print('')
    print('**** Phi ****')
    print(f'Number of bins: true phi = {phi_bins}, true r = {r_bins}, err phot = {phi_err_bins_phot}, err compt = {phi_err_bins_compt}')
    print('')

    ## photoelectric-like events
    print('Phot-like')
    file_name = output_folder + f'errmat_phi_phot_like.npz'
    h, eff, xmin, ymin, zmin, dx, dy, dz = fmc.compute_error_mat_3d(true_phi       [sel_phot_like],
                                                                    true_r         [sel_phot_like],
                                                                    diff_phi_matrix[sel_phot_like],
                                                                    bins   = (phi_bins,  r_bins,  phi_err_bins_phot),
                                                                    ranges = (phi_range, r_range, phi_err_range_phot))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, zmin=zmin, dx=dx, dy=dy, dz=dz)
    a = np.sum(h, axis=2)
    print(a.shape, a.shape[0]*a.shape[1], np.count_nonzero(a))


    ## compton-like events
    print('Compt-like')
    file_name = output_folder + f'errmat_phi_compt_like.npz'
    h, eff, xmin, ymin, zmin, dx, dy, dz = fmc.compute_error_mat_3d(true_phi       [sel_compt_like],
                                                                    true_r         [sel_compt_like],
                                                                    diff_phi_matrix[sel_compt_like],
                                                                    bins   = (phi_bins,  r_bins,  phi_err_bins_compt),
                                                                    ranges = (phi_range, r_range, phi_err_range_compt))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, zmin=zmin, dx=dx, dy=dy, dz=dz)
    a = np.sum(h, axis=2)
    print(a.shape, a.shape[0]*a.shape[1], np.count_nonzero(a))



    ### Z
    print('')
    print('**** Z ****')
    print(f'Number of bins: true z = {z_bins}, true r = {r_bins}, err phot = {z_err_bins_phot}, err compt = {z_err_bins_compt}')
    print('')

    ## photoelectric-like events
    print('Phot-like')
    file_name = output_folder + f'errmat_z_phot_like.npz'
    h, eff, xmin, ymin, zmin, dx, dy, dz = fmc.compute_error_mat_3d(true_z       [sel_phot_like],
                                                                    true_r       [sel_phot_like],
                                                                    diff_z_matrix[sel_phot_like],
                                                                    bins   = (z_bins,  r_bins,  z_err_bins_phot),
                                                                    ranges = (z_range, r_range, z_err_range_phot))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, zmin=zmin, dx=dx, dy=dy, dz=dz)
    a = np.sum(h, axis=2)
    print(a.shape, a.shape[0]*a.shape[1], np.count_nonzero(a))

    ## compton-like events
    print('Compt-like')
    file_name = output_folder + f'errmat_z_compt_like.npz'
    h, eff, xmin, ymin, zmin, dx, dy, dz = fmc.compute_error_mat_3d(true_z       [sel_compt_like],
                                                                    true_r       [sel_compt_like],
                                                                    diff_z_matrix[sel_compt_like],
                                                                    bins   = (z_bins,  r_bins,  z_err_bins_compt),
                                                                    ranges = (z_range, r_range, z_err_range_compt))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, zmin=zmin, dx=dx, dy=dy, dz=dz)
    a = np.sum(h, axis=2)
    print(a.shape, a.shape[0]*a.shape[1], np.count_nonzero(a))



    ### T
    print('')
    print('**** T ****')
    print(f'Number of bins: true t = {t_bins}, err phot = {t_err_bins_phot}, err compt = {t_err_bins_compt}')
    print('')

    ## photoelectric-like events
    print('Phot-like')
    file_name = output_folder + f'errmat_t_phot_like.npz'
    h, eff, xmin, ymin, dx, dy = fmc.compute_error_mat_2d(true_t               [sel_phot_like],
                                                          diff_reco_t_matrix[sel_phot_like],
                                                          bins   = (t_bins,  t_err_bins_phot),
                                                          ranges = (t_range, t_err_range_phot))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, dx=dx, dy=dy)
    a = np.sum(h, axis=1)
    print(a.shape, np.count_nonzero(a))

    ## compton-like events
    print('Compt-like')
    file_name = output_folder + f'errmat_t_compt_like.npz'
    h, eff, xmin, ymin, dx, dy = fmc.compute_error_mat_2d(true_t               [sel_compt_like],
                                                        diff_reco_t_matrix[sel_compt_like],
                                                        bins   = (t_bins,  t_err_bins_compt),
                                                        ranges = (t_range, t_err_range_compt))
    np.savez(file_name, errmat=h, eff=eff, xmin=xmin, ymin=ymin, dx=dx, dy=dy)
    a = np.sum(h, axis=1)
    print(a.shape, np.count_nonzero(a))


if __name__ == "__main__":

    input_folder  = str(sys.argv[1])
    output_folder = str(sys.argv[2])

    build_error_matrices(input_folder, output_folder)