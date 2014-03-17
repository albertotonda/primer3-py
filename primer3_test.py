import random
import resource
import unittest

from time import sleep 

from primer3 import bindings, wrappers


def _getMemUsage():
    """ Get current process memory usage in bytes """
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class TestLowLevelBindings(unittest.TestCase):

    def randArgs(self):
        self.seq1 = ''.join([random.choice('ATGC') for _ in
                             range(random.randint(20, 59))])
        self.seq2 = ''.join([random.choice('ATGC') for _ in
                             range(random.randint(20, 59))])
        self.mv_conc = random.uniform(1, 200)
        self.dv_conc = random.uniform(0, 40)
        self.dntp_conc = random.uniform(0, 20)
        self.dna_conc = random.uniform(0, 200)
        self.temp_c = random.randint(10, 70)
        self.max_loop = random.randint(10, 30)

    def test_calcTm(self):
        for x in range(25):
            self.randArgs()
            # The oligotm executable requires mv_conc and dna_conc to be ints
            # (technically longs... see oligotm_main.c vs. oligotm.c
            # discrepency)
            binding_tm = bindings.calcTm(
                                seq=self.seq1,
                                mv_conc=int(self.mv_conc),
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=int(self.dna_conc))
            wrapper_tm = wrappers.calcTm(
                                seq=self.seq1,
                                mv_conc=int(self.mv_conc),
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=int(self.dna_conc))
            self.assertEqual(int(binding_tm), int(wrapper_tm))

    def test_calcHairpin(self):
        for _ in range(25):
            self.randArgs()
            binding_res = bindings.calcHairpin(
                                seq=self.seq1,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            wrapper_res = wrappers.calcHairpin(
                                seq=self.seq1,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            if not wrapper_res:
                self.assertTrue(binding_res.no_structure == 1)
            else:
                self.assertEqual(int(binding_res.tm), int(wrapper_res.tm))

    def test_calcHomodimer(self):
        for _ in range(25):
            self.randArgs()
            binding_res = bindings.calcHomodimer(
                                seq=self.seq1,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            wrapper_res = wrappers.calcHomodimer(
                                seq=self.seq1,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            if not wrapper_res:
                self.assertTrue(binding_res.no_structure == 1)
            else:
                self.assertEqual(int(binding_res.tm), int(wrapper_res.tm))


    def test_calcHeterodimer(self):
        for _ in range(25):
            self.randArgs()
            binding_res = bindings.calcHeterodimer(
                                seq1=self.seq1,
                                seq2=self.seq2,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            wrapper_res = wrappers.calcHeterodimer(
                                seq1=self.seq1,
                                seq2=self.seq2,
                                mv_conc=self.mv_conc,
                                dv_conc=self.dv_conc,
                                dntp_conc=self.dntp_conc,
                                dna_conc=self.dna_conc,
                                temp_c=self.temp_c,
                                max_loop=self.max_loop)
            if not wrapper_res:
                self.assertTrue(binding_res.no_structure == 1)
            else:
                self.assertEqual(int(binding_res.tm), int(wrapper_res.tm))

    def test_memoryLeaks(self):
        sm = _getMemUsage()
        for x in range(1000):
            self.randArgs()
            bindings.calcHeterodimer(
                seq1=self.seq1,
                seq2=self.seq2,
                mv_conc=self.mv_conc,
                dv_conc=self.dv_conc,
                dntp_conc=self.dntp_conc,
                dna_conc=self.dna_conc,
                temp_c=self.temp_c,
                max_loop=self.max_loop)
        sleep(0.1)  # Pause for any GC
        em = _getMemUsage()
        print('\n\tMemory usage before 1k runs of calcHeterodimer: ', sm)
        print('\tMemory usage after 1k runs of calcHeterodimer:  ', em)
        print('\t\t\t\t\tDifference: \t', em-sm)
        if em-sm > 100:
            raise AssertionError('Memory usage increase after 1k runs of \n\t'
                                 'calcHeterodimer > 100 bytes -- potential \n\t'
                                 'memory leak (mem increase: {})'.format(em-sm))

class TestDesignBindings(unittest.TestCase):

    def testBindingRepeat(self):
        for x in range(20):
            bindings.designPrimers(
                {
                    'PRIMER_OPT_SIZE': 20,
                    'PRIMER_PICK_INTERNAL_OLIGO': 1,
                    'PRIMER_INTERNAL_MAX_SELF_END': 8,
                    'PRIMER_MIN_SIZE': 18,
                    'PRIMER_MAX_SIZE': 25,
                    'PRIMER_OPT_TM': 60.0,
                    'PRIMER_MIN_TM': 57.0,
                    'PRIMER_MAX_TM': 63.0,
                    'PRIMER_MIN_GC': 20.0,
                    'PRIMER_MAX_GC': 80.0,
                    'PRIMER_MAX_POLY_X': 100,
                    'PRIMER_INTERNAL_MAX_POLY_X': 100,
                    'PRIMER_SALT_MONOVALENT': 50.0,
                    'PRIMER_DNA_CONC': 50.0,
                    'PRIMER_MAX_NS_ACCEPTED': 0,
                    'PRIMER_MAX_SELF_ANY': 12,
                    'PRIMER_MAX_SELF_END': 8,
                    'PRIMER_PAIR_MAX_COMPL_ANY': 12,
                    'PRIMER_PAIR_MAX_COMPL_END': 8,
                },
                {
                    'PRIMER_PRODUCT_SIZE_RANGE': [75,100,100,125,125,150,150,175,175,200,200,225],
                    'SEQUENCE_ID': 'MH1000',
                    'SEQUENCE_TEMPLATE': 'GCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCCTACATTTTAGCATCAGTGAGTACAGCATGCTTACTGGAAGAGAGGGTCATGCAACAGATTAGGAGGTAAGTTTGCAAAGGCAGGCTAAGGAGGAGACGCACTGAATGCCATGGTAAGAACTCTGGACATAAAAATATTGGAAGTTGTTGAGCAAGTNAAAAAAATGTTTGGAAGTGTTACTTTAGCAATGGCAAGAATGATAGTATGGAATAGATTGGCAGAATGAAGGCAAAATGATTAGACATATTGCATTAAGGTAAAAAATGATAACTGAAGAATTATGTGCCACACTTATTAATAAGAAAGAATATGTGAACCTTGCAGATGTTTCCCTCTAGTAG',
                    'SEQUENCE_INCLUDED_REGION': [36,342]
                }
            )

    def testHuman(self):
        binding_res = bindings.designPrimers(
            {
                'PRIMER_OPT_SIZE': 20,
                'PRIMER_PICK_INTERNAL_OLIGO': 1,
                'PRIMER_INTERNAL_MAX_SELF_END': 8,
                'PRIMER_MIN_SIZE': 18,
                'PRIMER_MAX_SIZE': 25,
                'PRIMER_OPT_TM': 60.0,
                'PRIMER_MIN_TM': 57.0,
                'PRIMER_MAX_TM': 63.0,
                'PRIMER_MIN_GC': 20.0,
                'PRIMER_MAX_GC': 80.0,
                'PRIMER_MAX_POLY_X': 100,
                'PRIMER_INTERNAL_MAX_POLY_X': 100,
                'PRIMER_SALT_MONOVALENT': 50.0,
                'PRIMER_DNA_CONC': 50.0,
                'PRIMER_MAX_NS_ACCEPTED': 0,
                'PRIMER_MAX_SELF_ANY': 12,
                'PRIMER_MAX_SELF_END': 8,
                'PRIMER_PAIR_MAX_COMPL_ANY': 12,
                'PRIMER_PAIR_MAX_COMPL_END': 8,
            },
            {
                'PRIMER_PRODUCT_SIZE_RANGE': [75,100,100,125,125,150,150,175,175,200,200,225],
                'SEQUENCE_ID': 'MH1000',
                'SEQUENCE_TEMPLATE': 'GCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCCTACATTTTAGCATCAGTGAGTACAGCATGCTTACTGGAAGAGAGGGTCATGCAACAGATTAGGAGGTAAGTTTGCAAAGGCAGGCTAAGGAGGAGACGCACTGAATGCCATGGTAAGAACTCTGGACATAAAAATATTGGAAGTTGTTGAGCAAGTNAAAAAAATGTTTGGAAGTGTTACTTTAGCAATGGCAAGAATGATAGTATGGAATAGATTGGCAGAATGAAGGCAAAATGATTAGACATATTGCATTAAGGTAAAAAATGATAACTGAAGAATTATGTGCCACACTTATTAATAAGAAAGAATATGTGAACCTTGCAGATGTTTCCCTCTAGTAG',
                'SEQUENCE_INCLUDED_REGION': [36,342]
            }
        )
        wrapper_res = wrappers.runP3Main(
            {
                'PRIMER_OPT_SIZE': 20,
                'PRIMER_PICK_INTERNAL_OLIGO': 1,
                'PRIMER_INTERNAL_MAX_SELF_END': 8,
                'PRIMER_MIN_SIZE': 18,
                'PRIMER_MAX_SIZE': 25,
                'PRIMER_OPT_TM': 60.0,
                'PRIMER_MIN_TM': 57.0,
                'PRIMER_MAX_TM': 63.0,
                'PRIMER_MIN_GC': 20.0,
                'PRIMER_MAX_GC': 80.0,
                'PRIMER_MAX_POLY_X': 100,
                'PRIMER_INTERNAL_MAX_POLY_X': 100,
                'PRIMER_SALT_MONOVALENT': 50.0,
                'PRIMER_DNA_CONC': 50.0,
                'PRIMER_MAX_NS_ACCEPTED': 0,
                'PRIMER_MAX_SELF_ANY': 12,
                'PRIMER_MAX_SELF_END': 8,
                'PRIMER_PAIR_MAX_COMPL_ANY': 12,
                'PRIMER_PAIR_MAX_COMPL_END': 8,
                'PRIMER_PRODUCT_SIZE_RANGE': '75-100 100-125 125-150 150-175 175-200 200-225',
                'SEQUENCE_ID': 'MH1000',
                'SEQUENCE_TEMPLATE': 'GCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCCTACATTTTAGCATCAGTGAGTACAGCATGCTTACTGGAAGAGAGGGTCATGCAACAGATTAGGAGGTAAGTTTGCAAAGGCAGGCTAAGGAGGAGACGCACTGAATGCCATGGTAAGAACTCTGGACATAAAAATATTGGAAGTTGTTGAGCAAGTNAAAAAAATGTTTGGAAGTGTTACTTTAGCAATGGCAAGAATGATAGTATGGAATAGATTGGCAGAATGAAGGCAAAATGATTAGACATATTGCATTAAGGTAAAAAATGATAACTGAAGAATTATGTGCCACACTTATTAATAAGAAAGAATATGTGAACCTTGCAGATGTTTCCCTCTAGTAG',
                'SEQUENCE_INCLUDED_REGION': '36,342'
            }
        )
        for k, v in binding_res.items():
            try:
                self.assertEqual(str(wrapper_res.get(k)), v)
            except AssertionError:
                print('\nKey: {}, Wrapper output: {}, Binding output: {}'.format(k, wrapper_res.get(k), v))
                raise

if __name__ == '__main__':
    # unittest.main(verbosity=2)
    tl = unittest.TestLoader()
    lowLevelSuite = tl.loadTestsFromTestCase(TestLowLevelBindings)
    unittest.TextTestRunner(verbosity=2).run(lowLevelSuite)
    designSuite = tl.loadTestsFromTestCase(TestDesignBindings)
    unittest.TextTestRunner(verbosity=2).run(designSuite)
