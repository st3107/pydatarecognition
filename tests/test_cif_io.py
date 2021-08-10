from pathlib import Path
import numpy
import pytest
from testfixtures import TempDirectory
from pydatarecognition.cif_io import cif_read, user_input_read, _xy_write, rank_write
from pydatarecognition.powdercif import PowderCif
from tests.inputs.test_cifs import testciffiles_contents_expecteds

@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
def test_cif_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path)
    # build a PowderCif object with the right stuff in it for comparing with that
    #    built by the cif reader
    expected = PowderCif(
        cm[1].get("iucrid"), "deg", cm[1].get("ttheta"),
        cm[1].get("intensity"), wavelength=cm[1].get("wavelength"),
        wavel_units="nm"
    )
    assert actual.iucrid == expected.iucrid
    if cm[1].get('wavelength'):
        assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.ttheta, expected.ttheta)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength

    if actual.wavelength:
        with TempDirectory() as d:
            temp_dir = Path(d.path)
            cif_bitstream = bytearray(cm[0], 'utf8')
            d.write(f"test_cif.cif",
                    cif_bitstream)
            test_cif_path = temp_dir / f"test_cif.cif"
            cif_read(test_cif_path)
            actual = cif_read(test_cif_path)
        # build a PowderCif object with the right stuff in it for comparing with that
        #    built by the cif reader
            expected = PowderCif(
                cm[1].get("iucrid"), "invnm", cm[1].get("q"),
                cm[1].get("intensity"), wavelength=None
            )
        assert actual.iucrid == expected.iucrid
        assert numpy.allclose(actual.q, expected.q)
        assert numpy.allclose(actual.intensity, expected.intensity)
        assert actual.wavelength == expected.wavelength


testuserdata_contents_expecteds = [
    ("\
10.0413\t2037.0\n\
10.0913\t2212.0\n\
10.1413\t2155.0\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0]
                  ])
     ),
    ("\
10.0413\t2037.0\t55\n\
10.0913\t2212.0\t56\n\
10.1413\t2155.0\t57\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0],
                  [55, 56, 57]
                  ])
     )
]

@pytest.mark.parametrize("cm", testuserdata_contents_expecteds)
def test_user_input_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        userdata_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_userdata.txt",
                userdata_bitstream)
        test_userdata_path = temp_dir / f"test_userdata.txt"
        actual = user_input_read(test_userdata_path)
    expected = cm[1]
    numpy.testing.assert_array_equal(actual, expected)

pm = [
    (([1.0, 2, 3.2],
      [4, 5.5, 6]),
       '1.000000000000000000e+00\t4.000000000000000000e+00\n' \
       '2.000000000000000000e+00\t5.500000000000000000e+00\n' \
       '3.200000000000000178e+00\t6.000000000000000000e+00\n'),
]
@pytest.mark.parametrize("pm", pm)
def test__xy_write(pm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir / 'swallow.txt'
        x_array, y_array = numpy.array(pm[0][0]), numpy.array(pm[0][1])
        _xy_write(output_file_path, x_array, y_array)
        assert output_file_path.exists()
        expected = pm[1]
        with open(output_file_path) as f:
            actual = f.read()
        assert actual == expected


tab_char = '\t'

rw = [
    (([{'score': 0.99900, 'doi': '10.1107/S0108768102003476'},
       {'score': 0.999000, 'doi': '10.1107/S0108768102003476'},
       {'score': 0.70610, 'doi': '10.1107/S0108768102003476'},
       {'score': 0.70610, 'doi': '10.1107/S0108768102003476'},
       {'score': 0.70540, 'doi': '10.1107/S0108768101016330'},
       {'score': 0.70540, 'doi': '10.1107/S0108768101016330'},
       {'score': 0.65500, 'doi': '10.1107/S0108768101016330'},
       {'score': 0.65500, 'doi': '10.1107/S0108270102019637'},
       {'score': 0.32100, 'doi': '10.1107/S010876810402693X'},
       {'score': 0.32100, 'doi': '10.1107/S0108768105025991'},
       ]),
        'Rank\tScore\tDOI\t\t\t\t\t\t\tReference\n'
        '1\t\t0.9990\t10.1107/S0108768102003476\tUse of the Inorganic Crystal '
        'Structure Database as a problem solving tool, James A. Kaduk, Acta '
        'Crystallogr Sect B, v. 58, pp. 370-379, (2002).\n'
        '2\t\t0.9990\t10.1107/S0108768102003476\tUse of the Inorganic Crystal '
        'Structure Database as a problem solving tool, James A. Kaduk, Acta '
        'Crystallogr Sect B, v. 58, pp. 370-379, (2002).\n'
        '3\t\t0.7061\t10.1107/S0108768102003476\tUse of the Inorganic Crystal '
        'Structure Database as a problem solving tool, James A. Kaduk, Acta '
        'Crystallogr Sect B, v. 58, pp. 370-379, (2002).\n'
        '4\t\t0.7061\t10.1107/S0108768102003476\tUse of the Inorganic Crystal '
        'Structure Database as a problem solving tool, James A. Kaduk, Acta '
        'Crystallogr Sect B, v. 58, pp. 370-379, (2002).\n'
        '5\t\t0.7054\t10.1107/S0108768101016330\tStructure of C15-, C17- and '
        'C19-mono-acid ?-triacylglycerols, Robert B. Helmholdt, René Peschar, and '
        'Henk Schenk, Acta Crystallogr Sect B, v. 58, pp. 134-139, (2001).\n'
        '6\t\t0.7054\t10.1107/S0108768101016330\tStructure of C15-, C17- and '
        'C19-mono-acid ?-triacylglycerols, Robert B. Helmholdt, René Peschar, and '
        'Henk Schenk, Acta Crystallogr Sect B, v. 58, pp. 134-139, (2001).\n'
        '7\t\t0.6550\t10.1107/S0108768101016330\tStructure of C15-, C17- and '
        'C19-mono-acid ?-triacylglycerols, Robert B. Helmholdt, René Peschar, and '
        'Henk Schenk, Acta Crystallogr Sect B, v. 58, pp. 134-139, (2001).\n'
        '8\t\t0.6550\t10.1107/S0108270102019637\tLead tartrate from X-ray powder '
        'diffraction data, Dirk J. A. De Ridder, Kees Goubitz, Ed J. Sonneveld, Wim '
        'Molleman, and Henk Schenk, Acta Crystallogr C, v. 58, pp. m596-m598, '
        '(2002).\n'
        '9\t\t0.3210\t10.1107/S010876810402693X\tDetermination of the structure of '
        'the violet pigment C22H12Cl2N6O4 from a non-indexed X-ray powder diagram, '
        'Martin U. Schmidt, Martin Ermrich, and Robert E. Dinnebier, Acta Crystallogr '
        'Sect B, v. 61, pp. 37-45, (2005).\n'
        '10\t\t0.3210\t10.1107/S0108768105025991\tStructure and intermolecular '
        'interactions of glipizide from laboratory X-ray powder diffraction, Jonathan '
        'C. Burley, Acta Crystallogr Sect B, v. 61, pp. 710-716, (2005).\n'
     ),
]
@pytest.mark.parametrize("rw", rw)
def test_rank_write(rw):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir
        cif_ranks = rw[0]
        rank_write(cif_ranks, output_file_path)
        assert output_file_path.exists()
        expected = rw[1]
        with open(Path(output_file_path) / 'rank_PyCharm_Notepad++.txt') as f:
            actual = f.read()
        assert actual == expected
        # assert True

# End of file.